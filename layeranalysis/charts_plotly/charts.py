import plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import networkx as nx
# import pydot
import scipy # needed for sparse matrices in networkx
from networkx.drawing.nx_agraph import graphviz_layout
import json
import datetime
from sqlalchemy.sql import func, case, desc, null, asc, union_all, cast
from layeranalysis import layerapp, db
from timeit import default_timer as timer


def getNftSales(search_id):

    query_nft_sales = f'''SELECT  txn.block_timestamp AS 'Block time'
                      , txn.realized_nft_price AS 'Nft Price'
                      , txn.tx_typename AS 'Tx Type'
                      , txn.amount AS 'Amount'
                      , txn.nft_id AS 'NFT Id'
                      , to_Address.address AS 'To_Account'
                      , from_Address.address AS 'From_Account'
                      , txn.to_acct_id AS to_acct_id
                      , txn.from_acct_id AS from_acct_id
                      , e20.id as fee_id
                      , e20.symbol as fee_symbol
                FROM "transaction_nft" as txn
                INNER JOIN "collection" as coll
                    ON coll.id = txn.collection_id
                INNER JOIN "account" AS to_Address
                    ON to_Address.id = txn.to_acct_id
                INNER JOIN "account" AS from_Address
                    ON from_Address.id = txn.from_acct_id
                INNER JOIN "erc20tokens" as e20
                    ON txn.token_IDAS = e20.id
                Where coll.active = 1 
                    AND txn.tx_typename = 'TradeNFT'
           '''

    if len(search_id) == 66:  # NFT
        nft_id = search_id
        query_nft_sales = query_nft_sales + f''' and txn.nft_id = '{nft_id}' '''
        df = pd.read_sql(sql=query_nft_sales, con=db.engine)
    elif len(search_id) == 42:  # Account Address
        acct_address = search_id
        query_nft_sales = query_nft_sales + f''' AND (to_Address.address = '{acct_address}' OR from_Address.address = '{acct_address}'); '''
        df = pd.read_sql(sql=query_nft_sales, con=db.engine)
    elif len(search_id) > 0 and search_id.isdigit():
        acct_id = int(search_id)
        query_nft_sales = query_nft_sales + f''' AND (txn.to_acct_id = {acct_id} OR txn.from_acct_id = {acct_id} ) '''
        df = pd.read_sql(sql=query_nft_sales, con=db.engine)
    else:
        df = pd.read_sql(sql=query_nft_sales, con=db.engine)

    df = df.sort_values(by=['Block time', 'Nft Price'], ignore_index=True)
    # print(df['block_timestamp'][0], flush=True)
    df['Block time'] = pd.to_datetime(df['Block time'], infer_datetime_format=True)
    df['Updated Block time'] = df.loc[:, 'Block time']

    # Add a space inbetween overlapping points so the hover works (times are based on block time, so can have have multiple overlapping points)
    try:
        counter = 0
        duplicate = df[df.duplicated(['Block time', 'Nft Price'], keep=False)]
        last_ind = duplicate.index[0]  # skip first index in the spacing
        for ind in duplicate.index[1:]:
            if (duplicate.loc[ind, 'Block time'] == duplicate.loc[last_ind, 'Block time']) \
                    and (duplicate.loc[ind, 'Nft Price'] == duplicate.loc[last_ind, 'Nft Price']):
                counter += 1
                time_gap = int(500 * counter)
                df.loc[ind, 'Updated Block time'] = df['Updated Block time'][ind] + datetime.timedelta(milliseconds=time_gap)
            else:
                last_ind = ind
                counter = 0
    except Exception as err:
        print(err)

    if df['fee_symbol'].nunique() > 1:  # will need to come back if sales can be in something other than LRC or ETH
        # create scatter plot
        symbol1 = df['fee_symbol'].unique()[0]
        symbol2 = df['fee_symbol'].unique()[1]
        max1 = (df.loc[df['fee_symbol']==symbol1]['Nft Price'].max())
        min1 = (df.loc[df['fee_symbol']==symbol2]['Nft Price'].min())
        max2 = (df.loc[df['fee_symbol']==symbol1]['Nft Price'].max())
        min2 = (df.loc[df['fee_symbol']==symbol2]['Nft Price'].min())
        range1 = max1 - min1
        range2 = max2 - min2
        margin1 = range1 * 0.08
        margin2 = range2 * 0.08
        max1 = max1 + margin1
        max2 = max2 + margin2
        min1 = min1 - margin1
        min2 = min2 - margin2
        fig = px.scatter(df.loc[df['fee_symbol']==symbol1], x="Updated Block time", y="Nft Price",
                         hover_data=(
                         {"Block time": True, "Nft Price": True, "Amount": True, "NFT Id": True, "Tx Type": True,
                          "From_Account": True, "To_Account": True, "to_acct_id": True, "from_acct_id": True,
                          "Updated Block time": False}),
                         range_y=(min1, max1),
                         template="plotly_dark",
                         height=600,
                         render_mode="webgl")

        fig2 = px.scatter(df.loc[df['fee_symbol']==symbol2], x="Updated Block time", y="Nft Price",
                         hover_data=(
                         {"Block time": True, "Nft Price": True, "Amount": True, "NFT Id": True, "Tx Type": True,
                          "From_Account": True, "To_Account": True, "to_acct_id": True, "from_acct_id": True,
                          "Updated Block time": False}),
                         range_y=(min2, max2),
                         template="plotly_dark",
                         height=600,
                         render_mode="webgl")

        fig.update_traces(marker=dict(size=14, color='rgba(72,143,247,0.35)'
                                      , line=dict(width=2, color='rgba(13,110,253,0.95)')
                                      )
                          , selector=dict(mode='markers')
                          , name="NFT Priccccc data")

        fig2.update_traces(marker=dict(size=14, color='rgba(26, 237, 33,0.35)'
                                      , line=dict(width=2, color='rgba(95, 227, 100,0.8)')
                                      )
                           , selector=dict(mode='markers')
                           , name="yaxis2 data")

        fig2.update_traces(yaxis="y2")

        fig.add_traces(fig2.data).update_layout(yaxis={"title": "Nft Price (" + symbol1 + ")"}, yaxis2={"overlaying": "y", "side": "right", "title": "Nft Price (" + symbol2 + ")"})

    else:
        # create scatter plot
        max = (df['Nft Price'].max())
        min = (df['Nft Price'].min())
        range = max - min
        margin = range * 0.08
        max = max + margin
        min = min - margin
        fig = px.scatter(df, x="Updated Block time", y="Nft Price",
                         hover_data=({"Block time": True, "Nft Price": True, "Amount": True, "NFT Id": True, "Tx Type": True, "From_Account": True, "To_Account": True, "to_acct_id": True, "from_acct_id": True, "Updated Block time": False}),
                         range_y=(min, max),
                         template="plotly_dark",
                         height=600,
                         render_mode="webgl")

        fig.update_traces(marker=dict(size=14, color='rgba(72,143,247,0.35)'  # ,opacity=0.5
                                      , line=dict(width=2, color='rgba(13,110,253,0.95)')
                                      )
                          , selector=dict(mode='markers'))

    # Create a JSON representation of the graph
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON




def getNftNetwork(search_id):

    query_nft_txs = f'''SELECT  txn.nft_id AS 'Nft Id'
                                  , txn.tx_typename AS 'Tx Type'
                                  , txn.amount AS 'Amount'
                                  , txn.realized_nft_price AS 'Nft Price'
                                  , txn.block_timestamp AS 'Block time'
                                  , to_Address.address AS 'To_Account'
                                  , from_Address.address AS 'From_Account'
                                  , tok.symbol AS 'Token_Symbol'
                                  -- , txn.to_acct_id AS to_acct_id
                                  -- , txn.from_acct_id AS from_acct_id                      
                            FROM "transaction_nft" as txn
                            INNER JOIN "collection" as coll
                                ON coll.id = txn.collection_id
                            INNER JOIN "account" AS to_Address
                                ON to_Address.id = txn.to_acct_id
                            INNER JOIN "account" AS from_Address
                                ON from_Address.id = txn.from_acct_id
                            LEFT JOIN "ERC20Tokens" tok
                                on txn.token_IDAS = tok.id
                            Where coll.active = 1 
                                --AND txn.tx_typename = 'TradeNFT'
                                --AND txn.tx_typename <> 'MintNFT'
                                AND (txn.tx_typename = 'TradeNFT' OR txn.tx_typename = 'TransferNFT')
                       '''

    t0 = timer()
    if len(search_id) == 66:  # NFT
        nft_id = search_id
        query_nft_sales = query_nft_txs + f''' and txn.nft_id = '{nft_id}' '''
        df_nft_txs = pd.read_sql(sql=query_nft_sales, con=db.engine)
    elif len(search_id) == 42:  # Account Address
        acct_address = search_id
        query_nft_sales = query_nft_txs + f''' AND (to_Address.address = '{acct_address}' OR from_Address.address = '{acct_address}'); '''
        df_nft_txs = pd.read_sql(sql=query_nft_sales, con=db.engine)
    elif len(search_id) > 0 and search_id.isdigit():
        acct_id = int(search_id)
        print('1111111111111111111111111111111111111111111111111111111', flush=True)
        query_nft_sales = query_nft_txs + f''' AND (txn.to_acct_id = {acct_id} OR txn.from_acct_id = {acct_id} ) '''
        df_nft_txs = pd.read_sql(sql=query_nft_sales, con=db.engine)
    else:
        df_nft_txs = pd.read_sql(sql=query_nft_txs, con=db.engine)

    np_unique_address = np.unique(df_nft_txs[['To_Account', 'From_Account']].values)

    MG = nx.MultiGraph()
    MG.add_nodes_from(np_unique_address)

    t1 = timer()
    print('t1 - t0 = ' + str(t1 - t0), flush=True)

    for ind in range(df_nft_txs.shape[0]):
        MG.add_edges_from([(df_nft_txs.loc[ind, 'From_Account']
                                    , df_nft_txs.loc[ind, 'To_Account']
                                    , {'NftId': df_nft_txs.loc[ind, 'Nft Id']
                                        , 'Amount': df_nft_txs.loc[ind, 'Amount']
                                        , 'Price': df_nft_txs.loc[ind, 'Nft Price']
                                        , 'From_Account': df_nft_txs.loc[ind, 'From_Account']
                                        , 'TxType': df_nft_txs.loc[ind, 'Tx Type']
                                        , 'TokenSymbol': df_nft_txs.loc[ind, 'Token_Symbol']
                                       }
                                    )])

    t2 = timer()
    print('t2 - t1 = ' + str(t2 - t1), flush=True)
    print('t2 - t0 = ' + str(t2 - t0), flush=True)

    # Layout position for Network Graph
    # pos = nx.spring_layout(MG)  # 53 to 59 seconds
    # leaving in print timers for Debugging -> LRDebug
    t22 = timer()
    fixed = None
    # nfixed = {node: i for i, node in enumerate(MG)}
    # fixed = np.asarray([nfixed[node] for node in fixed if node in nfixed])
    A = nx.to_scipy_sparse_array(MG, weight="weight", dtype="f")
    print(A.shape, flush=True)
    print('t22 - t2 = ' + str(t22 - t2), flush=True)
    print('t22 - t0 = ' + str(t22 - t0), flush=True)
    print(df_nft_txs.shape, flush=True)
    print(MG.size(), flush=True)

    # This is the major performance hit (spring_layout)
    pos = nx.spring_layout(MG, threshold=1e-5, iterations=20, scale=3)
    # pos = nx.nx_agraph.graphviz_layout(MG, prog="dot")
    # pos = nx.nx_pydot.pydot_layout(MG)
    # pos = nx.kamada_kawai_layout(MG) #slow
    # pos = nx.spiral_layout(MG)
    # pos = nx.multipartite_layout(MG) #doesn't work, wants subsets

    t3 = timer()
    print('t3 - t2 = ' + str(t3 - t2), flush=True)
    print('t3 - t0 = ' + str(t3 - t0), flush=True)

    edge_x = []
    edge_y = []
    for edge in MG.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        mode='lines',
        hovertemplate='weight: %{text}<extra></extra>'
    )

    t4 = timer()
    print('t4 - t3 = ' + str(t4 - t3), flush=True)
    print('t4 - t0 = ' + str(t4 - t0), flush=True)


    node_x = []
    node_y = []
    for node in MG.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Earth',  # 'YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    t5 = timer()
    print('t5 - t4 = ' + str(t5 - t4), flush=True)
    print('t5 - t0 = ' + str(t5 - t0), flush=True)


    # Hover and Color
    node_adjacencies = []
    node_text = []
    edge_text = []
    for node, adjacencies in MG.adjacency():
        Amount = 0
        total_tx = 0
        amount_transfer_sent = 0
        amount_transfer_received = 0
        amount_trade_sold = 0
        amount_trade_bought = 0
        total_price_sold_lrc = 0.0
        total_price_sold_eth = 0.0
        total_price_bought_lrc = 0.0
        total_price_bought_eth = 0.0

        str_node_text = "Wallet Address: " + str(node)

        for neighbor in adjacencies.keys():
            for i in adjacencies[neighbor]:
                total_tx += 1

                if adjacencies[neighbor][i]['TxType'] == "TransferNFT":
                    if adjacencies[neighbor][i]['From_Account'] == node:
                        amount_transfer_sent += int(adjacencies[neighbor][i]['Amount'])
                    else:
                        amount_transfer_received += int(adjacencies[neighbor][i]['Amount'])

                elif adjacencies[neighbor][i]['TxType'] == "TradeNFT":
                    if adjacencies[neighbor][i]['From_Account'] == node:
                        amount_trade_sold += int(adjacencies[neighbor][i]['Amount'])

                        if adjacencies[neighbor][i]['TokenSymbol'] == 'LRC':
                            total_price_sold_lrc += float(adjacencies[neighbor][i]['Price'])
                        elif adjacencies[neighbor][i]['TokenSymbol'] == 'ETH':
                            total_price_sold_eth += float(adjacencies[neighbor][i]['Price'])
                    else:
                        amount_trade_bought += int(adjacencies[neighbor][i]['Amount'])
                        if adjacencies[neighbor][i]['TokenSymbol'] == 'LRC':
                            total_price_bought_lrc += float(adjacencies[neighbor][i]['Price'])
                        elif adjacencies[neighbor][i]['TokenSymbol'] == 'ETH':
                            total_price_bought_eth += float(adjacencies[neighbor][i]['Price'])

        if amount_transfer_sent != 0:
            str_node_text += "<br>Total # of Transfers From this Address : " + str(
                amount_transfer_sent)  # of Transfers Sent
        if amount_transfer_received != 0:
            str_node_text += "<br>Total # of Transfers To this Address : " + str(
                amount_transfer_received)  # of Transfers Received:

        # LRDEBUG Should probably combine total bough of LRC and ETH

        if total_price_sold_lrc != 0 or total_price_sold_eth != 0:
            str_node_text += "<br>Total # of NFTs Sold from this Address : " + str(
                amount_trade_sold)  # of NFTs Sold

            if total_price_sold_lrc != 0:
                # str_node_text += "<br>Total # of NFTs Sold from this Address : " + str(
                #     amount_trade_sold)  # of NFTs Sold:
                str_node_text += "<br>Price NFTs Sold: " + "{:10.3f}".format(
                    total_price_sold_lrc) + ' LRC'  # str(total_price_sold_lrc)

            if total_price_sold_eth != 0:
                # str_node_text += "<br>Total # of NFTs Sold from this Address : " + str(
                #     amount_trade_sold)  # of NFTs Sold:
                str_node_text += "<br>Price NFTs Sold: " + "{:10.6f}".format(
                    total_price_sold_eth) + ' ETH'  # str(total_price_sold_erc)


        if total_price_bought_lrc != 0 or total_price_bought_eth != 0:
            str_node_text += "<br>Total # of NFTs Bought from this Address : " + str(
                amount_trade_bought)  # of NFTs Bought:

            if total_price_bought_lrc != 0:
                # str_node_text += "<br>Total # of NFTs Bought from this Address : " + str(
                #     amount_trade_bought)  # of NFTs Bought:
                str_node_text += "<br>Price NFTs Bought: " + "{:10.3f}".format(
                    total_price_bought_lrc) + ' LRC'  # str(total_price_bought_lrc)

            if total_price_bought_eth != 0:
                # str_node_text += "<br>Total # of NFTs Bought from this Address : " + str(
                #     amount_trade_bought)  # of NFTs Bought:
                str_node_text += "<br>Price NFTs Bought: " + "{:10.6f}".format(
                    total_price_bought_eth) + ' ETH'  # str(total_price_bought_erc)

        node_adjacencies.append(int(total_tx))
        node_text.append(str_node_text)

    t6 = timer()
    print('t6 - t5 = ' + str(t6 - t5), flush=True)
    print('t6 - t0 = ' + str(t6 - t0), flush=True)


    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text
    edge_trace.text = edge_text

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        # title='<br>Network graph made with Python',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        autosize=True,
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    t7 = timer()
    print('t7 - t6 = ' + str(t7 - t6), flush=True)
    print('t7 - t0 = ' + str(t7 - t0), flush=True)

    fig.update_layout(autosize=True,
                      height=700,
                      template="plotly_dark")

    fig.update_traces(marker=dict(size=12), selector=dict(mode='markers'))

    t8 = timer()
    print('t8 - t7 = ' + str(t8 - t7), flush=True)
    print('t8 - t0 = ' + str(t8 - t0), flush=True)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    t9 = timer()
    print('t9 - t9 = ' + str(t9 - t8), flush=True)
    print('t9 - t0 = ' + str(t9 - t0), flush=True)

    return graphJSON
