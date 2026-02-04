#!/usr/bin/env python3
"""
USDC Bridge Script (CCTP)
Bridge USDC across blockchains using Circle's Cross-Chain Transfer Protocol.

Flow:
1. Approve USDC spend to TokenMessenger
2. Burn USDC on source chain via depositForBurn
3. Wait for Circle attestation
4. Mint USDC on destination chain via receiveMessage
"""

import argparse
import os
import time
import requests
from web3 import Web3
from eth_account import Account

# CCTP Contract Addresses
# TokenMessenger - handles deposits/burns
TOKEN_MESSENGER = {
    "ethereum": "0xBd3fa81B58Ba92a82136038B25aDec7066af3155",
    "ethereum_sepolia": "0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5",
    "base": "0x1682Ae6375C4E4A97e4B583BC394c861A46D8962",
    "base_sepolia": "0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5",
    "polygon": "0x9daF8c91AEFAE50b9c0E69629D3F6Ca40cA3B3FE",
    "arbitrum": "0x19330d10D9Cc8751218eaf51E8885D058642E08A",
    "arbitrum_sepolia": "0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5",
}

# MessageTransmitter - handles message receiving
MESSAGE_TRANSMITTER = {
    "ethereum": "0x0a992d191DEeC32aFe36203Ad87D7d289a738F81",
    "ethereum_sepolia": "0x7865fAfC2db2093669d92c0F33AeEF291086BEFD",
    "base": "0xAD09780d193884d503182aD4588450C416D6F9D4",
    "base_sepolia": "0x7865fAfC2db2093669d92c0F33AeEF291086BEFD",
    "polygon": "0xF3be9355363857F3e001be68856A2f96b4C39Ba9",
    "arbitrum": "0xC30362313FBBA5cf9163F0bb16a0e01f01A896ca",
    "arbitrum_sepolia": "0x7865fAfC2db2093669d92c0F33AeEF291086BEFD",
}

# CCTP Domain IDs (Circle's chain identifiers)
DOMAIN_IDS = {
    "ethereum": 0,
    "ethereum_sepolia": 0,
    "avalanche": 1,
    "optimism": 2,
    "arbitrum": 3,
    "arbitrum_sepolia": 3,
    "base": 6,
    "base_sepolia": 6,
    "polygon": 7,
}

# USDC addresses
USDC_ADDRESSES = {
    "ethereum": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "ethereum_sepolia": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
    "base": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "base_sepolia": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
    "polygon": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
    "arbitrum": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    "arbitrum_sepolia": "0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d",
}

DEFAULT_RPCS = {
    "ethereum": "https://eth.llamarpc.com",
    "ethereum_sepolia": "https://ethereum-sepolia-rpc.publicnode.com",
    "base": "https://base.llamarpc.com",
    "base_sepolia": "https://base-sepolia-rpc.publicnode.com",
    "polygon": "https://polygon.llamarpc.com",
    "arbitrum": "https://arbitrum.llamarpc.com",
    "arbitrum_sepolia": "https://arbitrum-sepolia-rpc.publicnode.com",
}

# Circle Attestation API
ATTESTATION_API = {
    "mainnet": "https://iris-api.circle.com/attestations",
    "testnet": "https://iris-api-sandbox.circle.com/attestations",
}

# ABIs
ERC20_APPROVE_ABI = [
    {
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
]

TOKEN_MESSENGER_ABI = [
    {
        "inputs": [
            {"name": "amount", "type": "uint256"},
            {"name": "destinationDomain", "type": "uint32"},
            {"name": "mintRecipient", "type": "bytes32"},
            {"name": "burnToken", "type": "address"}
        ],
        "name": "depositForBurn",
        "outputs": [{"name": "nonce", "type": "uint64"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

MESSAGE_TRANSMITTER_ABI = [
    {
        "inputs": [
            {"name": "message", "type": "bytes"},
            {"name": "attestation", "type": "bytes"}
        ],
        "name": "receiveMessage",
        "outputs": [{"name": "success", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]


def get_chain_key(chain: str, testnet: bool) -> str:
    if testnet:
        testnet_map = {
            "ethereum": "ethereum_sepolia",
            "base": "base_sepolia",
            "arbitrum": "arbitrum_sepolia",
        }
        return testnet_map.get(chain, chain)
    return chain


def address_to_bytes32(address: str) -> bytes:
    """Convert address to bytes32 (padded)."""
    return bytes.fromhex(address[2:].zfill(64))


def get_attestation(message_hash: str, testnet: bool = True, max_attempts: int = 30) -> dict:
    """Poll Circle's attestation API for the attestation."""
    api_url = ATTESTATION_API["testnet" if testnet else "mainnet"]
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{api_url}/{message_hash}")
            data = response.json()
            
            if data.get("status") == "complete":
                return {
                    "success": True,
                    "attestation": data.get("attestation"),
                    "message": data.get("message"),
                }
            
            print(f"   Waiting for attestation... ({attempt + 1}/{max_attempts})")
            time.sleep(10)
            
        except Exception as e:
            print(f"   Attestation API error: {e}")
            time.sleep(5)
    
    return {"error": "Attestation timeout"}


def bridge_usdc(to: str, amount: float, from_chain: str, to_chain: str, 
                testnet: bool = True, private_key: str = None) -> dict:
    """Bridge USDC from one chain to another using CCTP."""
    
    from_key = get_chain_key(from_chain, testnet)
    to_key = get_chain_key(to_chain, testnet)
    
    pk = private_key or os.getenv("USDC_PRIVATE_KEY")
    if not pk:
        return {"error": "No private key. Set USDC_PRIVATE_KEY env var."}
    
    # Get RPCs
    from_rpc = os.getenv(f"USDC_RPC_{from_chain.upper()}", DEFAULT_RPCS.get(from_key))
    to_rpc = os.getenv(f"USDC_RPC_{to_chain.upper()}", DEFAULT_RPCS.get(to_key))
    
    try:
        # Connect to source chain
        w3_from = Web3(Web3.HTTPProvider(from_rpc))
        account = Account.from_key(pk)
        sender = account.address
        
        # Get contract addresses
        usdc_addr = USDC_ADDRESSES.get(from_key)
        messenger_addr = TOKEN_MESSENGER.get(from_key)
        dest_domain = DOMAIN_IDS.get(to_key)
        
        if not all([usdc_addr, messenger_addr, dest_domain is not None]):
            return {"error": f"CCTP not supported for {from_key} -> {to_key}"}
        
        # Setup contracts
        usdc = w3_from.eth.contract(
            address=Web3.to_checksum_address(usdc_addr),
            abi=ERC20_APPROVE_ABI
        )
        messenger = w3_from.eth.contract(
            address=Web3.to_checksum_address(messenger_addr),
            abi=TOKEN_MESSENGER_ABI
        )
        
        decimals = usdc.functions.decimals().call()
        amount_raw = int(amount * (10 ** decimals))
        
        # Step 1: Approve TokenMessenger to spend USDC
        print(f"Step 1/4: Approving USDC spend...")
        nonce = w3_from.eth.get_transaction_count(sender)
        approve_tx = usdc.functions.approve(
            Web3.to_checksum_address(messenger_addr),
            amount_raw
        ).build_transaction({
            'from': sender,
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': w3_from.eth.gas_price,
            'chainId': w3_from.eth.chain_id,
        })
        signed = w3_from.eth.account.sign_transaction(approve_tx, pk)
        tx_hash = w3_from.eth.send_raw_transaction(signed.raw_transaction)
        w3_from.eth.wait_for_transaction_receipt(tx_hash)
        print(f"   Approved: {tx_hash.hex()}")
        
        # Step 2: Deposit for burn
        print(f"Step 2/4: Burning USDC on {from_key}...")
        recipient_bytes32 = address_to_bytes32(to)
        nonce = w3_from.eth.get_transaction_count(sender)
        
        burn_tx = messenger.functions.depositForBurn(
            amount_raw,
            dest_domain,
            recipient_bytes32,
            Web3.to_checksum_address(usdc_addr)
        ).build_transaction({
            'from': sender,
            'nonce': nonce,
            'gas': 300000,
            'gasPrice': w3_from.eth.gas_price,
            'chainId': w3_from.eth.chain_id,
        })
        signed = w3_from.eth.account.sign_transaction(burn_tx, pk)
        burn_hash = w3_from.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3_from.eth.wait_for_transaction_receipt(burn_hash)
        print(f"   Burned: {burn_hash.hex()}")
        
        # Step 3: Get message hash from logs and fetch attestation
        print(f"Step 3/4: Waiting for Circle attestation...")
        # Note: In production, you'd parse the MessageSent event to get the message hash
        # For now, we'll use a simplified approach
        message_hash = f"0x{burn_hash.hex()}"  # Simplified - should parse from logs
        
        attestation_result = get_attestation(message_hash, testnet)
        if "error" in attestation_result:
            return {
                "partial_success": True,
                "burn_tx": burn_hash.hex(),
                "error": attestation_result["error"],
                "note": "Burn successful. Attestation pending. Use status.py to complete."
            }
        
        # Step 4: Receive on destination chain
        print(f"Step 4/4: Minting USDC on {to_key}...")
        w3_to = Web3(Web3.HTTPProvider(to_rpc))
        transmitter = w3_to.eth.contract(
            address=Web3.to_checksum_address(MESSAGE_TRANSMITTER.get(to_key)),
            abi=MESSAGE_TRANSMITTER_ABI
        )
        
        nonce = w3_to.eth.get_transaction_count(sender)
        receive_tx = transmitter.functions.receiveMessage(
            bytes.fromhex(attestation_result["message"][2:]),
            bytes.fromhex(attestation_result["attestation"][2:])
        ).build_transaction({
            'from': sender,
            'nonce': nonce,
            'gas': 300000,
            'gasPrice': w3_to.eth.gas_price,
            'chainId': w3_to.eth.chain_id,
        })
        signed = w3_to.eth.account.sign_transaction(receive_tx, pk)
        receive_hash = w3_to.eth.send_raw_transaction(signed.raw_transaction)
        w3_to.eth.wait_for_transaction_receipt(receive_hash)
        
        return {
            "success": True,
            "amount": amount,
            "from_chain": from_key,
            "to_chain": to_key,
            "recipient": to,
            "burn_tx": burn_hash.hex(),
            "receive_tx": receive_hash.hex(),
        }
        
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Bridge USDC across chains via CCTP")
    parser.add_argument("--to", "-t", required=True, help="Recipient address")
    parser.add_argument("--amount", "-a", required=True, type=float, help="Amount in USDC")
    parser.add_argument("--from-chain", "-f", required=True,
                        choices=["ethereum", "base", "polygon", "arbitrum"],
                        help="Source chain")
    parser.add_argument("--to-chain", "-d", required=True,
                        choices=["ethereum", "base", "polygon", "arbitrum"],
                        help="Destination chain")
    parser.add_argument("--testnet", action="store_true", default=True,
                        help="Use testnet (default)")
    parser.add_argument("--mainnet", action="store_true",
                        help="Use mainnet (DANGER!)")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output as JSON")
    
    args = parser.parse_args()
    
    use_testnet = not args.mainnet
    
    if not use_testnet:
        confirm = input("⚠️  MAINNET BRIDGE! Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return
    
    print(f"🌉 Bridging {args.amount} USDC: {args.from_chain} → {args.to_chain}")
    print(f"   Recipient: {args.to}")
    print(f"   Network: {'testnet' if use_testnet else 'MAINNET'}")
    print()
    
    result = bridge_usdc(args.to, args.amount, args.from_chain, args.to_chain, use_testnet)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        elif result.get("partial_success"):
            print(f"⏳ Partial Success - Attestation Pending")
            print(f"   Burn TX: {result['burn_tx']}")
            print(f"   Note: {result['note']}")
        else:
            print(f"✅ Bridge Complete!")
            print(f"   Amount: {result['amount']} USDC")
            print(f"   Route: {result['from_chain']} → {result['to_chain']}")
            print(f"   Burn TX: {result['burn_tx']}")
            print(f"   Receive TX: {result['receive_tx']}")


if __name__ == "__main__":
    main()
