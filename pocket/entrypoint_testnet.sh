#!/usr/bin/env bash

function create_account_if_needed {
    if [ ! -f /home/app/.pocket/node_key.json ]
    then
	pocket accounts create
    fi
}

create_account_if_needed

# Exec is important here, we want to replace the current bash process
# so pocket keeps 1 as a PID within the container (so that signals are
# properly propagated).

exec pocket start --seeds="3487f08b9e915f347eb4372b406326ffbf13d82c@testnet-seed-1.nodes.pokt.network:4301,27f4295d1407d9512a25d7f2ea91d1a415660c16@testnet-seed-2.nodes.pokt.network:4302,0beb1a93fe9ce2a3b058b98614f1ed0f5ad664d5@testnet-seed-3.nodes.pokt.network:4303,8fd656162dbbe0402f3cef111d3ad8d2723eef8e@testnet-seed-4.nodes.pokt.network:4304,80100476b67fea2e94c6b2f72e40cf8f6062ed21@testnet-seed-5.nodes.pokt.network:4305,370edf0882e094e83d4087d5f8801bbf24f5d931@testnet-seed-6.nodes.pokt.network:4306,57aff5a049846d14e2dcc06fdcc241d7ebe6a3eb@testnet-seed-7.nodes.pokt.network:4307,545fb484643cf2efbcf01ee2b7bc793ef275cd84@testnet-seed-8.nodes.pokt.network:4308" --testnet
