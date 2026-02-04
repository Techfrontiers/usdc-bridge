#!/usr/bin/env python3
"""
USDC Send Script
Send USDC on the same chain.
"""

import argparse
import os
from web3 import Web3
from eth_account import Account

# USDC Contract Addresses (same as balance.py)
USDC_ADDRESSES = {
    "ethereum": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "ethereum_sepolia": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
    "base": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "base_sepolia": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
    "polygon": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
    "polygon_mumbai": "0x9999f7Fea5938fD3b1E26A12c3f2fb024e194f97",
    "arbitrum": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    "arbitrum_sepolia": "0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d",
}

DEFAULT_RPCS = {
    "ethereum": "https://eth.llamarpc.com",
    "ethereum_sepolia": "https://ethereum-sepolia-rpc.publicnode.com",
    "base": "https://base.llamarpc.com",
    "base_sepolia": "https://base-sepolia-rpc.publicnode.com",
    "polygon": "https://polygon.llamarpc.com",
    "polygon_mumbai": "https://polygon-mumbai-bor-rpc.publicnode.com",
    "arbitrum": "https://arbitrum.llamarpc.com",
    "arbitrum_sepolia": "https://arbitrum-sepolia-rpc.publicnode.com",
}

# ERC20 ABI for transfer
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
]


def get_chain_key(chain: str, testnet: bool) -> str:
    if testnet:
        testnet_map = {
            "ethereum": "ethereum_sepolia",
            "base": "base_sepolia",
            "polygon": "polygon_mumbai",
            "arbitrum": "arbitrum_sepolia",
        }
        return testnet_map.get(chain, chain)
    return chain


def send_usdc(to: str, amount: float, chain: str, testnet: bool = True, 
              private_key: str = None) -> dict:
    """Send USDC to an address on the same chain."""
    
    chain_key = get_chain_key(chain, testnet)
    
    # Get private key
    pk = private_key or os.getenv("USDC_PRIVATE_KEY")
    if not pk:
        return {"error": "No private key provided. Set USDC_PRIVATE_KEY env var."}
    
    # Get RPC
    rpc_env_key = f"USDC_RPC_{chain.upper()}"
    rpc_url = os.getenv(rpc_env_key, DEFAULT_RPCS.get(chain_key))
    
    if not rpc_url:
        return {"error": f"No RPC URL for chain: {chain_key}"}
    
    usdc_address = USDC_ADDRESSES.get(chain_key)
    if not usdc_address:
        return {"error": f"USDC not supported on chain: {chain_key}"}
    
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not w3.is_connected():
            return {"error": f"Could not connect to {chain_key} RPC"}
        
        # Get account from private key
        account = Account.from_key(pk)
        sender = account.address
        
        # Setup contract
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(usdc_address),
            abi=ERC20_ABI
        )
        
        # Get decimals and calculate amount
        decimals = contract.functions.decimals().call()
        amount_raw = int(amount * (10 ** decimals))
        
        # Build transaction
        nonce = w3.eth.get_transaction_count(sender)
        
        tx = contract.functions.transfer(
            Web3.to_checksum_address(to),
            amount_raw
        ).build_transaction({
            'from': sender,
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': w3.eth.gas_price,
            'chainId': w3.eth.chain_id,
        })
        
        # Sign and send
        signed = w3.eth.account.sign_transaction(tx, pk)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        
        return {
            "success": True,
            "tx_hash": tx_hash.hex(),
            "from": sender,
            "to": to,
            "amount": amount,
            "chain": chain_key,
            "testnet": testnet,
            "explorer": get_explorer_url(chain_key, tx_hash.hex()),
        }
        
    except Exception as e:
        return {"error": str(e)}


def get_explorer_url(chain_key: str, tx_hash: str) -> str:
    explorers = {
        "ethereum": f"https://etherscan.io/tx/{tx_hash}",
        "ethereum_sepolia": f"https://sepolia.etherscan.io/tx/{tx_hash}",
        "base": f"https://basescan.org/tx/{tx_hash}",
        "base_sepolia": f"https://sepolia.basescan.org/tx/{tx_hash}",
        "polygon": f"https://polygonscan.com/tx/{tx_hash}",
        "polygon_mumbai": f"https://mumbai.polygonscan.com/tx/{tx_hash}",
        "arbitrum": f"https://arbiscan.io/tx/{tx_hash}",
        "arbitrum_sepolia": f"https://sepolia.arbiscan.io/tx/{tx_hash}",
    }
    return explorers.get(chain_key, "")


def main():
    parser = argparse.ArgumentParser(description="Send USDC")
    parser.add_argument("--to", "-t", required=True, help="Recipient address")
    parser.add_argument("--amount", "-a", required=True, type=float, help="Amount in USDC")
    parser.add_argument("--chain", "-c", default="base",
                        choices=["ethereum", "base", "polygon", "arbitrum"],
                        help="Blockchain network")
    parser.add_argument("--testnet", action="store_true", default=True,
                        help="Use testnet (default: True)")
    parser.add_argument("--mainnet", action="store_true",
                        help="Use mainnet (DANGER!)")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output as JSON")
    
    args = parser.parse_args()
    
    use_testnet = not args.mainnet
    
    if not use_testnet:
        confirm = input("⚠️  MAINNET TRANSACTION! Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return
    
    result = send_usdc(args.to, args.amount, args.chain, use_testnet)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ USDC Sent Successfully!")
            print(f"   Amount: {result['amount']} USDC")
            print(f"   To: {result['to']}")
            print(f"   Chain: {result['chain']}")
            print(f"   TX: {result['explorer']}")


if __name__ == "__main__":
    main()
