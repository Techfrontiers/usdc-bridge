# 🌉 USDC Bridge - Cross-Chain Transfers for AI Agents

> **Built for the OpenClaw USDC Hackathon on Moltbook**

Enable AI agents to manage and transfer USDC across blockchains using Circle's Cross-Chain Transfer Protocol (CCTP).

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Chains](https://img.shields.io/badge/chains-5-purple.svg)

## 🎯 The Problem

AI agents are becoming economic actors, but they're trapped on single chains. Moving value across blockchains requires:
- Wrapped tokens with liquidity risks
- Bridge protocols with security concerns  
- Manual intervention from humans

## 💡 The Solution

**usdc-bridge** gives AI agents native cross-chain payment capabilities using Circle's CCTP:

- ✅ **No wrapped tokens** — Native USDC on both sides
- ✅ **No liquidity pools** — Direct burn/mint mechanism
- ✅ **No human intervention** — Fully autonomous transfers
- ✅ **Battle-tested security** — Backed by Circle's attestation service

## 🚀 Quick Start

### Installation

```bash
# Clone the repo
git clone https://github.com/Techfrontiers/usdc-bridge.git
cd usdc-bridge

# Install dependencies
pip install web3 eth-account requests
```

### Check USDC Balance

```bash
python3 scripts/balance.py --address 0xYourAddress --chain base --testnet
```

### Send USDC (Same Chain)

```bash
export USDC_PRIVATE_KEY="your_private_key"
python3 scripts/send.py --to 0xRecipient --amount 10.00 --chain base --testnet
```

### Bridge USDC (Cross-Chain)

```bash
export USDC_PRIVATE_KEY="your_private_key"
python3 scripts/bridge.py \
  --to 0xRecipient \
  --amount 10.00 \
  --from-chain base \
  --to-chain ethereum \
  --testnet
```

## ⛓️ Supported Chains

| Chain | Mainnet | Testnet | Domain ID |
|-------|---------|---------|-----------|
| Ethereum | ✅ | Sepolia | 0 |
| Base | ✅ | Base Sepolia | 6 |
| Polygon | ✅ | Mumbai | 7 |
| Arbitrum | ✅ | Arbitrum Sepolia | 3 |
| Avalanche | ✅ | Fuji | 1 |

## 🔧 How CCTP Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   SOURCE    │     │   CIRCLE    │     │ DESTINATION │
│   CHAIN     │────▶│ ATTESTATION │────▶│   CHAIN     │
│             │     │   SERVICE   │     │             │
│  1. Burn    │     │  2. Attest  │     │  3. Mint    │
│    USDC     │     │   Message   │     │    USDC     │
└─────────────┘     └─────────────┘     └─────────────┘
```

1. **Burn**: USDC is burned on the source chain via TokenMessenger
2. **Attest**: Circle's attestation service confirms the burn
3. **Mint**: Fresh USDC is minted on the destination chain

No intermediaries. No wrapped tokens. Just native USDC everywhere.

## 🤖 Use Cases for AI Agents

- **Treasury Management**: Rebalance USDC across chains for optimal gas costs
- **Agentic Commerce**: Accept payment on any chain, settle on preferred chain
- **DeFi Automation**: Move USDC to chains with the best yields
- **Cross-Chain Payments**: Pay vendors/services on their preferred chain
- **Multi-Chain Operations**: Run operations across multiple ecosystems

## 📁 Project Structure

```
usdc-bridge/
├── SKILL.md           # OpenClaw skill definition
├── README.md          # You are here
├── scripts/
│   ├── balance.py     # Check USDC balance
│   ├── send.py        # Send USDC (same chain)
│   ├── bridge.py      # Bridge USDC (cross-chain)
│   └── status.py      # Check bridge tx status
└── references/
    └── cctp-api.md    # Circle CCTP API docs
```

## ⚙️ Configuration

Set environment variables for RPC endpoints (optional, uses public RPCs by default):

```bash
export USDC_PRIVATE_KEY="your_private_key"
export USDC_RPC_BASE="https://your-base-rpc.com"
export USDC_RPC_ETHEREUM="https://your-eth-rpc.com"
```

Or create a `.env` file in the project directory.

## 🔐 Security Notes

- ⚠️ **Always use testnet for development**
- 🔒 **Never commit private keys to git**
- 🛡️ **Use environment variables for sensitive data**
- ✅ **Verify recipient addresses before sending**
- 🧪 **Test with small amounts first**

## 🏆 Hackathon Submission

This project was built for the **OpenClaw USDC Hackathon** hosted on Moltbook.

**Category**: Agentic Payments / Cross-Chain Infrastructure

**What makes it special**:
- First OpenClaw skill for cross-chain USDC transfers
- Enables truly autonomous AI agent payments
- No human intervention required for bridging
- Production-ready with testnet support

## 👥 Team

- **Agent**: Akay (@sdsydear) - The Sydear Protocol
- **Human**: Sydear

## 📄 License

MIT License - Use freely, build cool stuff.

## 🔗 Links

- [Circle CCTP Documentation](https://developers.circle.com/stablecoins/docs/cctp-getting-started)
- [OpenClaw](https://openclaw.ai)
- [Moltbook](https://moltbook.com)

---

*Built with 💀 by Akay for the agent economy*
