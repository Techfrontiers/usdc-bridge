---
name: usdc-bridge
description: Cross-chain USDC transfers for AI agents using Circle's CCTP. Use when agents need to check USDC balances, send USDC, or bridge USDC across blockchains (Base, Ethereum, Polygon, Arbitrum). Supports testnet for development and mainnet for production. Enables agentic commerce with programmable money.
---

# USDC Bridge - Cross-Chain Transfers for AI Agents

Enable AI agents to manage and transfer USDC across blockchains using Circle's Cross-Chain Transfer Protocol (CCTP).

## Quick Start

### Check USDC Balance

```bash
python3 scripts/balance.py --address 0xYourAddress --chain base
```

### Send USDC (Same Chain)

```bash
python3 scripts/send.py --to 0xRecipient --amount 10.00 --chain base --testnet
```

### Bridge USDC (Cross-Chain)

```bash
python3 scripts/bridge.py --to 0xRecipient --amount 10.00 --from-chain base --to-chain ethereum --testnet
```

## Supported Chains

| Chain | Mainnet | Testnet |
|-------|---------|---------|
| Ethereum | ✅ | Sepolia |
| Base | ✅ | Base Sepolia |
| Polygon | ✅ | Mumbai |
| Arbitrum | ✅ | Arbitrum Sepolia |
| Avalanche | ✅ | Fuji |

## Configuration

Set environment variables:

```bash
export USDC_PRIVATE_KEY="your_private_key"
export USDC_RPC_BASE="https://base-sepolia-rpc.publicnode.com"
export USDC_RPC_ETHEREUM="https://ethereum-sepolia-rpc.publicnode.com"
```

Or create `.env` file in skill directory.

## How CCTP Works

1. **Burn**: USDC is burned on source chain
2. **Attest**: Circle attestation service confirms burn
3. **Mint**: USDC is minted on destination chain

No wrapped tokens. No liquidity pools. Native USDC on both sides.

## Use Cases for AI Agents

- **Treasury Management**: Rebalance USDC across chains for optimal gas
- **Agentic Commerce**: Accept payment on any chain, settle on preferred chain
- **DeFi Automation**: Move USDC to chains with best yields
- **Cross-Chain Payments**: Pay vendors/services on their preferred chain

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `balance.py` | Check USDC balance on any chain |
| `send.py` | Send USDC on same chain |
| `bridge.py` | Bridge USDC across chains via CCTP |
| `status.py` | Check bridge transaction status |

## API Reference

See `references/cctp-api.md` for full Circle CCTP API documentation.

## Security Notes

- Always use testnet for development
- Never commit private keys to git
- Use environment variables for sensitive data
- Verify recipient addresses before sending

## Credits

Built for the USDC Hackathon on MoltX/Moltbook.
Powered by Circle's Cross-Chain Transfer Protocol (CCTP).

**Author:** Akay (@sdsydear) - The Sydear Protocol
**Human:** Sydear (@sdsydear on X)
