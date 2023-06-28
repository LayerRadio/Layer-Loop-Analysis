
# Layer-Loop-Analysis
A Loopring NFT Collection and Wallet Dashboard

![LLA_Alpha_HomePage_2023-06-20_16-13-48](https://github.com/LayerRadio/Layer-Loop-Analysis/assets/122059499/b2583a25-f5df-4e7d-8451-b0602e6beee3)

## Overview

Layer Loop Analysis is a Dashboard that analyzes Loopring NFT Collections and Wallets (Wallets to come Soon). 

Layer Loop Analysis fetches transaction data from the Loopring GraphQL Subgraph. At the moment, there is no API key needed, but functionality may be added in the future, which will require it. Due to using the Subgraph, data is not available until the block has been written (30-45 minutes from L2 transaction). Also, the collections are currently based off of a Contract Address (and are categorized by the Loopring Collection)

This is a Dockerized Flask app with a local SQLite database. There will be discussions in the future on whether to host and make API (cost and security factors). There is benefit to the user being able to have data stored locally for those that want to run their own additional analysis. However, there is a a technical barrier to entry and there's been consideration of ways to minimize this. 

Requests, code contributions, and further discussion is encouraged. This will help shape the direction of the project. 

The initial motivation came from trying to track down scammers and having to perform all of those searches manually. However, as building began, it became more of goal to develop something that the community could use to perfom thier own analysis and view collections.

This dashboard uses data from the Loopring GraphQL subgraph (no API key is needed at the moment, the Loopring API may be added in the future, or in a separate new app)

NFT Collections are grouped by the Contract Address. This can be a little confusing for legacy collections since these contracts can have multiple Loopring collections. Adding in Loopring collections has been considered, but decisions on the best way to introduce them and track their changes have yet to be made.

Please Note that since this is in the **Alpha** stage, the database schema is likely to change. There are plans to introduce db migration in the future for upgrades, however, it is unlikely that it will happen in the first initial upgrades, so the data may need to be re-downloaded again. The way docker is currently set up was also made with the idea that it is in Development stage.



## Prerequisites

- [Docker](https://docs.docker.com/engine/install/) is installed. (Note: Docker needs to be **running**.)
- [Git](https://github.com/git-guides/install-git/) is installed.


## Install and Running Steps

### Install

#### Clone Layer-Loop-Analysis

```sh
git clone https://github.com/LayerRadio/Layer-Loop-Analysis.git
cd Layer-Loop-Analysis
```


#### Build Docer image
```sh
docker image build -t layer-analysis .
```

Note: this step will be updated in the near future


#### Start Layer Loop Analysis Docker

```sh
docker compose up
```

If you don't want the logs showing, then add the flag 'd' ```docker compose up -d```


#### Navigate to App

Then in an internet browser, navigate to 
[http://localhost/home](http://localhost/home)


#### Stopping Layer Loop Analysis Docker

```sh
docker compose down
```


#### Logs Layer Loop Analysis Docker
```sh
docker compose logs -f 
```

Note: remove the '-f' flag to not have the logs continuous. 


#### Updating Layer Loop Analysis Docker

More on this soon. Currently, discussing the best delivery process. 


## Using the Dashboard

### Collections

#### Get Data

Navigate to Collection -> Get Data (or url [http://localhost/collection](http://localhost/collection)). In the search field, put in the collection address and press the button `Fetch Collection Tx`. This search field will update a collection if it has already been downloaded. Note: the initial download can take a few seconds per unique NFT. Fetching a collection can take several hours. The Loopheads took about 40 minutes

A loading screen will display. Do not navigate away from this screen. If you don't have time to download, be sure to delete the partially downloaded collection before attempting to re-download it. 

To select Collections for the Dashboard, use the checkboxes and use the button ``'Load All Selected items in the Dashboard'``. In the table, the column labeled `Active` will switch to `Yes`.

You can also Update and Delete collections with the checkboxes.

![LLA_Alpha_GetData_2023-06-23_11-49](https://github.com/LayerRadio/Layer-Loop-Analysis/assets/122059499/15dfb8ae-e13f-4049-aa2f-c56bda947d73)

#### Dashboard

Once the Collections have been selected on the Get Data page, navigate to the Dashboard page to see the Dashboard. The first card will have summarized data (note: hover over the data for explanations). The card to the right will have a graph showing the sales of the collection. It currently only displays sales in LRC and ETH (they seem to be the primary tokens used for transactions, however, if there have been sales using other tokens, please reach out, as this can be changed).

![LLA_Alpha_Dashboard_1_2023-06-23_11-56](https://github.com/LayerRadio/Layer-Loop-Analysis/assets/122059499/ac642e31-b6c3-4ccf-9a0c-c8ead600de05)

Below this, you will find a network graph of the Collection(s). It includes all transactions except minting. For large collections, this can take a minute or 2 to display. Due to performance, this may need to be moved to it's own page (especially for wallet analysis).

<p align="center">
  <img alt="Dark" src=https://github.com/LayerRadio/Layer-Loop-Analysis/assets/122059499/712a9dde-6eaf-4ace-a1b0-b12d0e853eaa width="45%">
&nbsp; &nbsp; &nbsp; &nbsp;
  <img alt="Dark" src=https://github.com/LayerRadio/Layer-Loop-Analysis/assets/122059499/95716d3f-c5e5-46c8-ad81-eb7c320b4bde width="45%">
</p>

#### Raw Data

Collections are based on the contract address. This means that if there are multiple loopring collections, than they will appear just under the contract address. In the future, looking to add this in, but will need to add in API calls. This seems to mainly affect Legacy Loopring collections.


### Wallets

Coming Soon


## Features

Layer Loop Analysis

- Downloads Entire Collections (based on Contract Address)
- Allows for downloading the CSV of Raw Data Collection
- Overall statistics\numbers
- Search Tables by Wallet Addresses and Ids
- Price Graph
- Network Graph
- Sales and Transactions Tables
- Can perform analysis on multiple collections at once


## Important note

- This is in Alpha stage and is being released at this stage so that the community can have input. There is still further testing needed for accuracy. 

- Legacy Collections and unnamed collections will have 'None' in the Name. 


## Future

The future development will be taking in request and ideas from the community.

- Take requests/suggestions from the Community
- Tracking and Analysis for Wallets
- Improved error handling
- Add support for Loopring Collections (this will be based on request and discussion)
- Add analysis, graphs and tables (this will be based on request and discussion)
- Add Ajax calls to charts and tables
- Investigate NetworkGraphs for improved performance and functionality (considering moving to it's own section due to performance)
- File/Folder restructuring
- Code clean up
- Set up CI


## Support

If you like the dashboard, please grab an NFT or 2 on LoopExchange ShiddyZoo - Meet the Zoo on LoopExchange [https://loopexchange.art/collection/shiddyzoo](https://loopexchange.art/collection/shiddyzoo) 

Or LayerRadio.eth - [0xb36a4675be59cd8ef2cbef43ebfb06c053e41848](https://explorer.loopring.io/account/192416)

## Testing

If you are unfamiliar with Loopring, can run this against the following collections

- 0xb07e92e0a9dc45711a9ef4c6cccfcde798de75ff
- 0x0a6f4b318b9397670a9926acbddbb9a3361b71bd
- 0x43778ce982ef806376f9f6b87f426ba9f4e9ee3a (this one takes a few minutes to download)
- 0x1cacc96e5f01e2849e6036f25531a9a064d2fb5f (this one takes 30 minutes to an hour to download)


## Credits

Special thanks to [Fudgey](https://github.com/fudgebucket27) for his work all his work and contributions on Community Loopring code projects and giving me guidance on Loopring's Subgraph. Subgraph queries were modeled from [Lexplorer](https://github.com/fudgebucket27/Lexplorer)

[Cobmin](https://github.com/cobmin) for his work on Loopring Collections and please check out [Maize](https://github.com/cobmin/Maize)

[LoopringSharp](https://github.com/taranasus/LoopringSharp)

[LooPyMinty](https://github.com/Montspy/LooPyMinty)

[Miguel Grinberg](https://github.com/miguelgrinberg), can also check out his blog with topics on Flask

[README.md](README.md) is partially modeled off of Taiko's Docs [taiko-mono](https://github.com/taikoxyz/taiko-mono/blob/main/packages/website/pages/docs/guides/run-a-node.mdx)


# Licensing

## Code

All scripts and scene files are distributed under the [MIT license](LICENSE.md).  
Copyright held by Layer Radio LLC.


## Asset

All of the photos, gifs and art assets of this project (files in ``images_LR/`` ie [``layeranalysis/static/images_LR``](https://github.com/LayerRadio/Layer-Loop-Analysis/tree/main/layeranalysis/static/images_LR)) have been made available to this project by Layer Radio LLC and are copyrighted; any other use must be authorized by the creator which holds all the rights for those photos.

Any other file of this project is available under the MIT license


### Note on Asset license 

The license for the 2 art assets is currently restrictive. However, I am considering either removing the art, or putting the art under a different license, such as the CCA. The ``loading_sz.gif`` made me happy and was fun to put in, but doesn't really add anything and is heavy, so will likely remove in future versions if people are wanting more freedom with Layer Loop Analysis.


# Video Tutorial

This is a youtube video tutorial on how to use Layer Loop Analysis 

[https://www.youtube.com/watch?v=adp33az-rac](https://www.youtube.com/watch?v=adp33az-rac)




