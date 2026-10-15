# Categories

The data set covers the local food system: anything that produces, makes, distributes,
sells or serves food, or supplies the people who do. No entity is too large or too small
if a category fits it, and if none fits we add one. What a *public* application shows is
a separate decision (see "Data versus display" below).

Rules live in `scripts/scrape/categories.py` (data label -> filter group) and are enforced
by `scripts/tests/test_categories.py`. A record can carry several labels, primary first.

## Labels

| Role | Label | Use for |
|---|---|---|
| Grow | On-Farm / Ranch Sales, Farm Products (online), Roadside Market, U-Pick, CSA Farm, Agritourism, Wholesale Grower | existing |
| Grow | **Flower Farm** *(new)* | cut-flower and other flower growers |
| Grow | **Plant Nursery** *(new)* | nurseries, native-plant growers, greenhouses selling plants (retail garden centers keep `Garden Center / Greenhouse`) |
| Grow | **Seed Company** *(new)* | seed growers and sellers |
| Make | Food Maker, Bakery, Winery, Meat Producer & Packer | existing |
| Make | **Cottage Food** *(new)* | home-based licensed food makers (jams, baking, dips, ferments) |
| Make | **Food Processor** *(new)* | custom processors, mills, dairies and plants that process others' product |
| Make | **Brewery / Distillery** *(new)* | breweries, distilleries, cideries |
| Distribute | Food Hub, Community Food Hub | existing |
| Distribute | **Distributor / Aggregator** *(new)* | wholesalers, distributors, resellers and aggregators of local product |
| Distribute | **Market Vendor** *(new)* | verified producers who sell through farmers markets and have no separate sales location |
| Sell / serve | Farmers' Market, Farm Store, Grocery Store, Restaurant, Caterer | existing |
| Sell / serve | **Food Truck**, **Cafe / Coffee Shop** *(new)* | mobile and counter-service food businesses |
| Support | Food Bank, Organization | existing |
| Support | **Ag Input Supplier** *(new)* | feed, soil, compost, worm castings, equipment |

Not yet categories (add when records need them): institutional buyers (schools,
hospitals), livestock merchants, hay and forage, cideries separate from breweries.

## Suggested mapping for Colorado Proud business types
Today the Colorado Proud importer only keeps the types in `TYPE_CATEGORIES`. These
currently unmapped types now have a home (counts from `category_counts.csv`):

| Colorado Proud type | New label |
|---|---|
| Food Manufacturer (243), Manufacturer (105) | Food Maker / Food Processor |
| Wholesaler (95), Distributor (33), Merchant / Merchandiser (19), Wholesale Market (13), Buyer | Distributor / Aggregator |
| Food Truck (64), Mobile Food Stand / Cart (27) | Food Truck |
| Coffee Shop (34) | Cafe / Coffee Shop |
| Brewery (21), Distillery (19), Beer | Brewery / Distillery |
| Ag Input Supplier (20) | Ag Input Supplier |
| Retailer (101) | needs a look (retail of what?) |

Importing these is a separate step: it would add several hundred records.

## Data versus display
The data set may hold every location; applications filter. A public map shows only
places that advertise a sales channel. New labels are in the data but a group only appears
on the live map once `index.html` styles it (unstyled groups are skipped), so adding a
category never changes the public map by itself.
