---
title: "Weekly Paper: Helix"
date: 2018-11-10T11:49:28+08:00
tags: [consensus, "distributedSystem"]
series: ["Weekly Paper"]
draft: false
description: "Reading notes of paper: Helix, A Scalable and Fair Consensus Algorithm"
comment: true
share: true
hljs: false
hljsLanguages: []
mathjax: false
---

[Orbs - Read the Helix Consensus Algorithm White Paper](https://orbs.com/helix-consensus-whitepaper/)

Hazel is a **Byzantine fault-tolerant** and **scalable** consensus algorithm for the fair ordering of transactions among nodes in a distributed network.

It assumed that:

- Node-node connections are assumed to be strongly synchronous.
- There is a known bound for the faulty nodes.

It is scalable because the PBFT committee size is bounded.

Helix archives fairness in these aspects.

- Committee selection relies on reputation and a random seed.
- Transactions are randomly selected when they are encrypted.

Both committee election and transactions sampling utilize a random seed derived from the previous decrypted block.

Helix nodes validate block transaction by checking the distribution overlap with local transaction pool.
