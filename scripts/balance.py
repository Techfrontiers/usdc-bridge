#!/usr/bin/env python3
"""
USDC Balance Checker
Check USDC balance on any supported chain.
"""

import argparse
import os
from web3 import Web3

# USDC Contract Addresses
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

# Default RPC endpoints (public, rate-limited)
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

# ERC20 ABI (minimal for balanceOf)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
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
    """Get the chain key for addresses/RPCs."""
    if testnet:
        testnet_map = {
            "ethereum": "ethereum_sepolia",
            "base": "base_sepolia",
            "polygon": "polygon_mumbai",
            "arbitrum": "arbitrum_sepolia",
        }
        return testnet_map.get(chain, chain)
    return chain


def get_balance(address: str, chain: str, testnet: bool = False) -> dict:
    """Get USDC balance for an address on a specific chain."""
    chain_key = get_chain_key(chain, testnet)
    
    # Get RPC URL from env or use default
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
        
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(usdc_address),
            abi=ERC20_ABI
        )
        
        balance_raw = contract.functions.balanceOf(
            Web3.to_checksum_address(address)
        ).call()
        
        decimals = contract.functions.decimals().call()
        balance = balance_raw / (10 ** decimals)
        
        return {
            "address": address,
            "chain": chain_key,
            "testnet": testnet,
            "balance": balance,
            "balance_raw": balance_raw,
            "decimals": decimals,
            "usdc_contract": usdc_address,
        }
        
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Check USDC balance")
    parser.add_argument("--address", "-a", required=True, help="Wallet address")
    parser.add_argument("--chain", "-c", default="base", 
                        choices=["ethereum", "base", "polygon", "arbitrum"],
                        help="Blockchain network")
    parser.add_argument("--testnet", "-t", action="store_true",
                        help="Use testnet")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output as JSON")
    
    args = parser.parse_args()
    
    result = get_balance(args.address, args.chain, args.testnet)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            network = f"{result['chain']} ({'testnet' if result['testnet'] else 'mainnet'})"
            print(f"💰 USDC Balance on {network}")
            print(f"   Address: {result['address']}")
            print(f"   Balance: {result['balance']:.6f} USDC")


if __name__ == "__main__":
    main()
