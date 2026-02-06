# StarRupture Production Calculator

A python 3 program that can be used to determine what inputs, and machines are necessary to craft a specific item with a specific rate.
The output of the program is a summary of required items as well as a production tree starting with the requested item and working backwards
to the raw materials that start the chain.

> [!NOTE]
> The item database is not complete. I wrote this program to help me when playing the game and I
> have compiled the database by hand from the game as I unlocked items and buildings. As such, the
> database is only complete up to the point I have played. If you are further on in the game, you
> can add the missing items to the data files.

> [!IMPORTANT]
> Developed using Python version 3.12 on Linux. Ran successfully on Windows 11 in command terminal.

## Command line
```
usage: StarRupture Calculator [-h] (-i ITEM NAME | -s FILENAME | --dump_items)
                              [-c COUNT | -m NUM MACHINES] [-d DEPTH]
                              [--genspec FILENAME] [-u]

Calculates the machines and intermediate items required to craft requested
item.

options:
  -h, --help            show this help message and exit
  -i ITEM NAME, --item ITEM NAME
                        Requested item. Mutually exclusive with option 'spec'.
  -s FILENAME, --spec FILENAME
                        Item specifier as a JSON file. Mutually exclusive with
                        option 'item'. JSON comments aren't supported.
  --dump_items          Output the available items and exit.
  -c COUNT, --count COUNT
                        Requested number of items. When no number is specified
                        either here or within the JSON spec, the output of a
                        single machine is requested. Mututally exclusive with
                        option 'machines'.
  -m NUM MACHINES, --machines NUM MACHINES
                        Calculate for the number of machines producing the
                        requested item. Mututally exclusive with option
                        'count'.
  -d DEPTH, --depth DEPTH
                        Limit production chain printing depth. Valid values
                        are 0 to maxint. When less than 1, no limit. When 1,
                        prints out the request machine and immediate inputs.
                        When 2, prints out the request machine, it's inputs,
                        and their inputs. Etc.

Generate spec file:
  Generate a template item specification file for an item.

  --genspec FILENAME    Instead of performing a calculation, write out a spec
                        file for requested item. The provided parameter is the
                        spec file name. The parameter '--item' sets the item
                        in the spec file. The parameter '--count' sets the
                        request per minute. If count not provided, the ipm of
                        a single machine is set.
  -u, --use_input       When specified, the written template file will include
                        an inputs section.
```

## Calculating the production chain of an item

The following command will calculate the requirements to produce "glass" at a rate that can be output by a single machine.
```sh
python3 srcalc.py --item glass
```
outputs
```
╔═════════════════════════════╗
║                             ║
║ REQUESTING: 20 ipm of glass ║
║                             ║
╚═════════════════════════════╝

                     Provided   Required   Num
Item                 IPM        IPM        Machines        Machine              Heat Cost
---------------------------------------------------------------------------------------------------
calcium block                60      13.33       0.22 ( 1) smelter                 3    100 bbm
calcium ore                 120      13.33       0.11 ( 1) ore excavator           3     80 bbm
calcium powder               60      40.00       0.67 ( 1) furnace                 8    200 bbm
glass                        20      20.00       1.00 ( 1) furnace                 8    200 bbm
helium-3                    240      20.00       0.08 ( 1) helium-3 extractor     60    250 bbm

┌────────────────────────────────────────────────┐
│ furnace (x1)  [heat 8] [200 bbm]               │
│ glass                                          │
│ prov: 20    (20/machine)                       │
│ req:  20.00 (1.000 machines)                   │
└────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ furnace (x1)  [heat 8] [200 bbm]               │
|   │ calcium powder                                 │
|   │ prov: 60    (60/machine)                       │
|   │ req:  40.00 (0.667 machines)                   │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ smelter (x1)  [heat 3] [100 bbm]               │
|   |   │ calcium block                                  │
|   |   │ prov: 60    (60/machine)                       │
|   |   │ req:  13.33 (0.222 machines)                   │
|   |   └────────────────────────────────────────────────┘
|   |   |   ┌────────────────────────────────────────────────┐
|   |   |   │ ore excavator (x1)  [heat 3] [80 bbm]          │
|   |   |   │ calcium ore                                    │
|   |   |   │ prov: 120    (120/machine)                     │
|   |   |   │ req:  13.33 (0.111 machines)                   │
|   |   |   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ helium-3 extractor (x1)  [heat 60] [250 bbm]   │
|   │ helium-3                                       │
|   │ prov: 240    (240/machine)                     │
|   │ req:  20.00 (0.083 machines)                   │
|   └────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> The game has multiple variants for raw materials that provide a different rate of production.
> My data file contains the rates for each variant: impure, pure and the unnamed one which I call
> normal. The calculations are made with only the production rate of "normal" ores.

### Summary section of output
The summary table provides the total requirements for each item in alphabetical order.
| Column | Description |
|--------|-------------|
| Item | Name of item |
| Provided IPM | The rate, in items per minute, that is output by all the machines crafting that item. |
| Required IPM | The rate, in items per minute, that the item is consumed by the production chain. |
| Num Machines | The number of machines that are required to satisfy the required IPM. The value in parenthesis is the number of machines that have to be built. |
| Machine | Name of the machine crafting the item. |
| Heat | The total heat added by constructing the number of machines. |
| Cost | The total cost in building materials to construct the number of machines. |

### Tree view of production chain
Starting at the requested item, each machine of the production chain is represented by a block in a tree graph. The input providers are machine
blocks listed under and indented.

A machine block consists of 4 lines:
1. The machine name, number of machines in parenthesis, heat and material costs.
2. The name of the item produced by the machine.
3. The amount, in items per minute, that the number of machines are capable of producing. The number within the parenthesis is the amount produced per machine.
4. The amount, in items per minute, required by the parent machine. The number within the parenthesis is the ratio of the required to the provided amounts.

## Calculating the production chain of an item for a specific rate

The following command will calculate the requirements to produce "glass" at a specific rate.
The rate is specified by the `--count` option.
```sh
python3 srcalc.py -i glass --count 35
```

```
╔═════════════════════════════╗
║                             ║
║ REQUESTING: 35 ipm of glass ║
║                             ║
╚═════════════════════════════╝

                     Provided   Required   Num
Item                 IPM        IPM        Machines        Machine              Heat Cost
---------------------------------------------------------------------------------------------------
calcium block                60      23.33       0.39 ( 1) smelter                 3    100 bbm
calcium ore                 120      23.33       0.19 ( 1) ore excavator           3     80 bbm
calcium powder              120      70.00       1.17 ( 2) furnace                16    400 bbm
glass                        40      35.00       1.75 ( 2) furnace                16    400 bbm
helium-3                    240      35.00       0.15 ( 1) helium-3 extractor     60    250 bbm

┌────────────────────────────────────────────────┐
│ furnace (x2)  [heat 16] [400 bbm]              │
│ glass                                          │
│ prov: 40    (20/machine)                       │
│ req:  35.00 (1.750 machines)                   │
└────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ furnace (x2)  [heat 16] [400 bbm]              │
|   │ calcium powder                                 │
|   │ prov: 120    (60/machine)                      │
|   │ req:  70.00 (1.167 machines)                   │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ smelter (x1)  [heat 3] [100 bbm]               │
|   |   │ calcium block                                  │
|   |   │ prov: 60    (60/machine)                       │
|   |   │ req:  23.33 (0.389 machines)                   │
|   |   └────────────────────────────────────────────────┘
|   |   |   ┌────────────────────────────────────────────────┐
|   |   |   │ ore excavator (x1)  [heat 3] [80 bbm]          │
|   |   |   │ calcium ore                                    │
|   |   |   │ prov: 120    (120/machine)                     │
|   |   |   │ req:  23.33 (0.194 machines)                   │
|   |   |   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ helium-3 extractor (x1)  [heat 60] [250 bbm]   │
|   │ helium-3                                       │
|   │ prov: 240    (240/machine)                     │
|   │ req:  35.00 (0.146 machines)                   │
|   └────────────────────────────────────────────────┘
```

## Calculating the production chain of an item for a specific number of machines

The following command will calculate the requirements to produce "glass" using a specific number
of machines. The number of machines is specified by the `--machines` option. This will result
in an item rate set by multiplying the rate of a single machine by the number of machines.
The option `--machines` is mutually exclusive with `--count`.
```sh
python3 srcalc.py -i glass --machines 7
```
Results in a rate of 140 ipm, from 7 times 20:
```
╔══════════════════════════════╗
║                              ║
║ REQUESTING: 140 ipm of glass ║
║                              ║
╚══════════════════════════════╝

                     Provided   Required   Num
Item                 IPM        IPM        Machines        Machine              Heat Cost
---------------------------------------------------------------------------------------------------
calcium block               120      93.33       1.56 ( 2) smelter                 6    200 bbm
calcium ore                 120      93.33       0.78 ( 1) ore excavator           3     80 bbm
calcium powder              300     280.00       4.67 ( 5) furnace                40   1000 bbm
glass                       140     140.00       7.00 ( 7) furnace                56   1400 bbm
helium-3                    240     140.00       0.58 ( 1) helium-3 extractor     60    250 bbm

┌────────────────────────────────────────────────┐
│ furnace (x7)  [heat 56] [1400 bbm]             │
│ glass                                          │
│ prov: 140    (20/machine)                      │
│ req:  140.00 (7.000 machines)                  │
└────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ furnace (x5)  [heat 40] [1000 bbm]             │
|   │ calcium powder                                 │
|   │ prov: 300    (60/machine)                      │
|   │ req:  280.00 (4.667 machines)                  │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ smelter (x2)  [heat 6] [200 bbm]               │
|   |   │ calcium block                                  │
|   |   │ prov: 120    (60/machine)                      │
|   |   │ req:  93.33 (1.556 machines)                   │
|   |   └────────────────────────────────────────────────┘
|   |   |   ┌────────────────────────────────────────────────┐
|   |   |   │ ore excavator (x1)  [heat 3] [80 bbm]          │
|   |   |   │ calcium ore                                    │
|   |   |   │ prov: 120    (120/machine)                     │
|   |   |   │ req:  93.33 (0.778 machines)                   │
|   |   |   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ helium-3 extractor (x1)  [heat 60] [250 bbm]   │
|   │ helium-3                                       │
|   │ prov: 240    (240/machine)                     │
|   │ req:  140.00 (0.583 machines)                  │
|   └────────────────────────────────────────────────┘
```

## Limiting the depth of the tree graph output

When planning the production of an item, you may want to only see the direct
inputs of a few levels. This option doesn't affect the calculation and only
stops the tree output at the specified level. The option to set a depth limit
is `--depth`.
```sh
python3 srcalc.py -i glass --depth 1
```
outputs
```
┌────────────────────────────────────────────────┐
│ furnace (x1)  [heat 8] [200 bbm]               │
│ glass                                          │
│ prov: 20    (20/machine)                       │
│ req:  20.00 (1.000 machines)                   │
└────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ furnace (x1)  [heat 8] [200 bbm]               │
|   │ calcium powder                                 │
|   │ prov: 60    (60/machine)                       │
|   │ req:  40.00 (0.667 machines)                   │
|   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ helium-3 extractor (x1)  [heat 60] [250 bbm]   │
|   │ helium-3                                       │
|   │ prov: 240    (240/machine)                     │
|   │ req:  20.00 (0.083 machines)                   │
|   └────────────────────────────────────────────────┘
```
and
```sh
python3 srcalc.py -i glass --depth 2
```
outputs
```
┌────────────────────────────────────────────────┐
│ furnace (x1)  [heat 8] [200 bbm]               │
│ glass                                          │
│ prov: 20    (20/machine)                       │
│ req:  20.00 (1.000 machines)                   │
└────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ furnace (x1)  [heat 8] [200 bbm]               │
|   │ calcium powder                                 │
|   │ prov: 60    (60/machine)                       │
|   │ req:  40.00 (0.667 machines)                   │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ smelter (x1)  [heat 3] [100 bbm]               │
|   |   │ calcium block                                  │
|   |   │ prov: 60    (60/machine)                       │
|   |   │ req:  13.33 (0.222 machines)                   │
|   |   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ helium-3 extractor (x1)  [heat 60] [250 bbm]   │
|   │ helium-3                                       │
|   │ prov: 240    (240/machine)                     │
|   │ req:  20.00 (0.083 machines)                   │
|   └────────────────────────────────────────────────┘
```
Here's an example for a more complex item:
```sh
python3 srcalc.py -i valve --depth 1
```
```
┌────────────────────────────────────────────────┐
│ mega press (x1)  [heat 15] [80 ibm]            │
│ valve                                          │
│ prov: 6    (6/machine)                         │
│ req:  6.00 (1.000 machines)                    │
└────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ mega press (x1)  [heat 15] [80 ibm]            │
|   │ nozzle                                         │
|   │ prov: 12    (12/machine)                       │
|   │ req:  6.00 (0.500 machines)                    │
|   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ fabricator (x1)  [heat 5] [140 bbm]            │
|   │ titanium beam                                  │
|   │ prov: 20    (20/machine)                       │
|   │ req:  18.00 (0.900 machines)                   │
|   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ furnace (x1)  [heat 8] [200 bbm]               │
|   │ titanium housing                               │
|   │ prov: 30    (30/machine)                       │
|   │ req:  6.00 (0.200 machines)                    │
|   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ fabricator (x1)  [heat 5] [140 bbm]            │
|   │ titanium rod                                   │
|   │ prov: 30    (30/machine)                       │
|   │ req:  12.00 (0.400 machines)                   │
|   └────────────────────────────────────────────────┘
```
```sh
python3 srcalc.py -i valve --depth 2
```
```
┌────────────────────────────────────────────────┐
│ mega press (x1)  [heat 15] [80 ibm]            │
│ valve                                          │
│ prov: 6    (6/machine)                         │
│ req:  6.00 (1.000 machines)                    │
└────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ mega press (x1)  [heat 15] [80 ibm]            │
|   │ nozzle                                         │
|   │ prov: 12    (12/machine)                       │
|   │ req:  6.00 (0.500 machines)                    │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ furnace (x1)  [heat 8] [200 bbm]               │
|   |   │ heat resistant sheet                           │
|   |   │ prov: 15    (15/machine)                       │
|   |   │ req:  12.00 (0.800 machines)                   │
|   |   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ helium-3 extractor (x1)  [heat 60] [250 bbm]   │
|   |   │ helium-3                                       │
|   |   │ prov: 240    (240/machine)                     │
|   |   │ req:  6.00 (0.025 machines)                    │
|   |   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ fabricator (x2)  [heat 10] [280 bbm]           │
|   |   │ stabilizer                                     │
|   |   │ prov: 20    (10/machine)                       │
|   |   │ req:  12.00 (1.200 machines)                   │
|   |   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ fabricator (x1)  [heat 5] [140 bbm]            │
|   │ titanium beam                                  │
|   │ prov: 20    (20/machine)                       │
|   │ req:  18.00 (0.900 machines)                   │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ smelter (x1)  [heat 3] [100 bbm]               │
|   |   │ titanium bar                                   │
|   |   │ prov: 60    (60/machine)                       │
|   |   │ req:  18.00 (0.300 machines)                   │
|   |   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ furnace (x1)  [heat 8] [200 bbm]               │
|   │ titanium housing                               │
|   │ prov: 30    (30/machine)                       │
|   │ req:  6.00 (0.200 machines)                    │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ fabricator (x1)  [heat 5] [140 bbm]            │
|   |   │ titanium beam                                  │
|   |   │ prov: 20    (20/machine)                       │
|   |   │ req:  6.00 (0.300 machines)                    │
|   |   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ fabricator (x1)  [heat 5] [140 bbm]            │
|   |   │ titanium sheet                                 │
|   |   │ prov: 60    (60/machine)                       │
|   |   │ req:  12.00 (0.200 machines)                   │
|   |   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ fabricator (x1)  [heat 5] [140 bbm]            │
|   │ titanium rod                                   │
|   │ prov: 30    (30/machine)                       │
|   │ req:  12.00 (0.400 machines)                   │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ smelter (x1)  [heat 3] [100 bbm]               │
|   |   │ titanium bar                                   │
|   |   │ prov: 60    (60/machine)                       │
|   |   │ req:  12.00 (0.200 machines)                   │
|   |   └────────────────────────────────────────────────┘
```
```sh
python3 srcalc.py -i valve --depth 3
```
```
┌────────────────────────────────────────────────┐
│ mega press (x1)  [heat 15] [80 ibm]            │
│ valve                                          │
│ prov: 6    (6/machine)                         │
│ req:  6.00 (1.000 machines)                    │
└────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ mega press (x1)  [heat 15] [80 ibm]            │
|   │ nozzle                                         │
|   │ prov: 12    (12/machine)                       │
|   │ req:  6.00 (0.500 machines)                    │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ furnace (x1)  [heat 8] [200 bbm]               │
|   |   │ heat resistant sheet                           │
|   |   │ prov: 15    (15/machine)                       │
|   |   │ req:  12.00 (0.800 machines)                   │
|   |   └────────────────────────────────────────────────┘
|   |   |   ┌────────────────────────────────────────────────┐
|   |   |   │ furnace (x1)  [heat 8] [200 bbm]               │
|   |   |   │ glass                                          │
|   |   |   │ prov: 20    (20/machine)                       │
|   |   |   │ req:  12.00 (0.600 machines)                   │
|   |   |   └────────────────────────────────────────────────┘
|   |   |   ┌────────────────────────────────────────────────┐
|   |   |   │ fabricator (x1)  [heat 5] [140 bbm]            │
|   |   |   │ titanium sheet                                 │
|   |   |   │ prov: 60    (60/machine)                       │
|   |   |   │ req:  24.00 (0.400 machines)                   │
|   |   |   └────────────────────────────────────────────────┘
|   |   |   ┌────────────────────────────────────────────────┐
|   |   |   │ fabricator (x1)  [heat 5] [140 bbm]            │
|   |   |   │ wolfram plate                                  │
|   |   |   │ prov: 60    (60/machine)                       │
|   |   |   │ req:  12.00 (0.200 machines)                   │
|   |   |   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ helium-3 extractor (x1)  [heat 60] [250 bbm]   │
|   |   │ helium-3                                       │
|   |   │ prov: 240    (240/machine)                     │
|   |   │ req:  6.00 (0.025 machines)                    │
|   |   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ fabricator (x2)  [heat 10] [280 bbm]           │
|   |   │ stabilizer                                     │
|   |   │ prov: 20    (10/machine)                       │
|   |   │ req:  12.00 (1.200 machines)                   │
|   |   └────────────────────────────────────────────────┘
|   |   |   ┌────────────────────────────────────────────────┐
|   |   |   │ fabricator (x2)  [heat 10] [280 bbm]           │
|   |   |   │ rotor                                          │
|   |   |   │ prov: 20    (10/machine)                       │
|   |   |   │ req:  12.00 (1.200 machines)                   │
|   |   |   └────────────────────────────────────────────────┘
|   |   |   ┌────────────────────────────────────────────────┐
|   |   |   │ fabricator (x1)  [heat 5] [140 bbm]            │
|   |   |   │ titanium rod                                   │
|   |   |   │ prov: 30    (30/machine)                       │
|   |   |   │ req:  24.00 (0.800 machines)                   │
|   |   |   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ fabricator (x1)  [heat 5] [140 bbm]            │
|   │ titanium beam                                  │
|   │ prov: 20    (20/machine)                       │
|   │ req:  18.00 (0.900 machines)                   │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ smelter (x1)  [heat 3] [100 bbm]               │
|   |   │ titanium bar                                   │
|   |   │ prov: 60    (60/machine)                       │
|   |   │ req:  18.00 (0.300 machines)                   │
|   |   └────────────────────────────────────────────────┘
|   |   |   ┌────────────────────────────────────────────────┐
|   |   |   │ ore excavator (x1)  [heat 3] [80 bbm]          │
|   |   |   │ titanium ore                                   │
|   |   |   │ prov: 120    (120/machine)                     │
|   |   |   │ req:  18.00 (0.150 machines)                   │
|   |   |   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ furnace (x1)  [heat 8] [200 bbm]               │
|   │ titanium housing                               │
|   │ prov: 30    (30/machine)                       │
|   │ req:  6.00 (0.200 machines)                    │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ fabricator (x1)  [heat 5] [140 bbm]            │
|   |   │ titanium beam                                  │
|   |   │ prov: 20    (20/machine)                       │
|   |   │ req:  6.00 (0.300 machines)                    │
|   |   └────────────────────────────────────────────────┘
|   |   |   ┌────────────────────────────────────────────────┐
|   |   |   │ smelter (x1)  [heat 3] [100 bbm]               │
|   |   |   │ titanium bar                                   │
|   |   |   │ prov: 60    (60/machine)                       │
|   |   |   │ req:  6.00 (0.100 machines)                    │
|   |   |   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ fabricator (x1)  [heat 5] [140 bbm]            │
|   |   │ titanium sheet                                 │
|   |   │ prov: 60    (60/machine)                       │
|   |   │ req:  12.00 (0.200 machines)                   │
|   |   └────────────────────────────────────────────────┘
|   |   |   ┌────────────────────────────────────────────────┐
|   |   |   │ smelter (x1)  [heat 3] [100 bbm]               │
|   |   |   │ titanium bar                                   │
|   |   |   │ prov: 60    (60/machine)                       │
|   |   |   │ req:  6.00 (0.100 machines)                    │
|   |   |   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ fabricator (x1)  [heat 5] [140 bbm]            │
|   │ titanium rod                                   │
|   │ prov: 30    (30/machine)                       │
|   │ req:  12.00 (0.400 machines)                   │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ smelter (x1)  [heat 3] [100 bbm]               │
|   |   │ titanium bar                                   │
|   |   │ prov: 60    (60/machine)                       │
|   |   │ req:  12.00 (0.200 machines)                   │
|   |   └────────────────────────────────────────────────┘
|   |   |   ┌────────────────────────────────────────────────┐
|   |   |   │ ore excavator (x1)  [heat 3] [80 bbm]          │
|   |   |   │ titanium ore                                   │
|   |   |   │ prov: 120    (120/machine)                     │
|   |   |   │ req:  12.00 (0.100 machines)                   │
|   |   |   └────────────────────────────────────────────────┘
```

## Printing the list of known items

To print the names of the known items, use the `--dump_items` option. This
option is mutually exclusive with `--item` and `--spec`.
```sh
python3 srcalc.py --dump_items
```
This outputs a single column list of item names in alphabetical order.

## Using a specification file

Instead of specifying the item name on the command line, you can read a
specification file that includes the requested item name, optionally includes
the requested IPM, and optionally provides a set of existing inputs into the
production chain.

### Specification file format
The specification file is a JSON text file. Comments within the file are not
supported and the comments in the example are only for documentation purposes
and would result in an error if used in the actual spec file.

```json
{
    "request": {
        // Name of item to be crafted.
        // Required.
        "item": "",

        // Optional number of items to craft per minute. This can be overridden by the
        // value specified on the program command line. When set to a value less than 1,
        // or not provided, the default is to use the number of items that can be produced
        // by a single machine per minute.
        "items_per_minute": 0
    },

    // Optional list of available items that can be fed into the production chain.
    "inputs": [
        {
            // Provided items are intended to be used as an input for a specific node in the
            // production chain. The array identifies the node in the chain by the item names
            // starting at the machine producing the requested item, and working backwards down the
            // manufacturing chain.
            //
            // For example, when crafting 'electronics' and existing supply of inductors is
            // available, then "for_item" will be: ["electronics"]. However, if a certain amount
            // of calcite sheets are available to produce ceramics for synthetic silicon, then
            // "for_item" will be: ["electronics", "synthetic silicon", "ceramics"]
            // Required.
            "for_item": [""],
            // The item that is provided as an input from an existing manufacturing site.
            // Required.
            "provided_item": "",
            // The items per minute that can be provided.
            // Required.
            "provided_ipm": 0
        }
    ]
}
```

### Using a specification file to calculate a production chain
```sh
python3 srcalc.py --spec glass.json
```
glass.json
```json
{
    "request": {
        "item": "glass",
        "items_per_minute": 12
    }
}
```

```
╔═════════════════════════════╗
║                             ║
║ REQUESTING: 12 ipm of glass ║
║                             ║
╚═════════════════════════════╝

                     Provided   Required   Num
Item                 IPM        IPM        Machines        Machine              Heat Cost
---------------------------------------------------------------------------------------------------
calcium block                60       8.00       0.13 ( 1) smelter                 3    100 bbm
calcium ore                 120       8.00       0.07 ( 1) ore excavator           3     80 bbm
calcium powder               60      24.00       0.40 ( 1) furnace                 8    200 bbm
glass                        20      12.00       0.60 ( 1) furnace                 8    200 bbm
helium-3                    240      12.00       0.05 ( 1) helium-3 extractor     60    250 bbm

┌────────────────────────────────────────────────┐
│ furnace (x1)  [heat 8] [200 bbm]               │
│ glass                                          │
│ prov: 20    (20/machine)                       │
│ req:  12.00 (0.600 machines)                   │
└────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ furnace (x1)  [heat 8] [200 bbm]               │
|   │ calcium powder                                 │
|   │ prov: 60    (60/machine)                       │
|   │ req:  24.00 (0.400 machines)                   │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ smelter (x1)  [heat 3] [100 bbm]               │
|   |   │ calcium block                                  │
|   |   │ prov: 60    (60/machine)                       │
|   |   │ req:  8.00 (0.133 machines)                    │
|   |   └────────────────────────────────────────────────┘
|   |   |   ┌────────────────────────────────────────────────┐
|   |   |   │ ore excavator (x1)  [heat 3] [80 bbm]          │
|   |   |   │ calcium ore                                    │
|   |   |   │ prov: 120    (120/machine)                     │
|   |   |   │ req:  8.00 (0.067 machines)                    │
|   |   |   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ helium-3 extractor (x1)  [heat 60] [250 bbm]   │
|   │ helium-3                                       │
|   │ prov: 240    (240/machine)                     │
|   │ req:  12.00 (0.050 machines)                   │
|   └────────────────────────────────────────────────┘
```

### Using a specification file to calculate a production chain with existing inputs
In this example, the "calcium block" input into the machine crafting "calcium powder" is being
supplied from an existing production facility. The existing production facility can provide
100 items of "calcium block" per minute which is more than the required input into
"calcium powder" so no further calculations are required for that input.
```sh
python3 srcalc.py --spec glass.json
```
glass.json
```json
{
    "request": {
        "item": "glass"
    },
    "inputs":[
      {
        "for_item":["glass", "calcium powder"],
        "provided_item": "calcium block",
        "provided_ipm": 100
      }
    ]
}
```
The summary changes to list only the items crafted in the production chain and excludes the items
provided as inputs.
```
╔═════════════════════════════╗
║                             ║
║ REQUESTING: 20 ipm of glass ║
║                             ║
╚═════════════════════════════╝

                     Provided   Required   Num
Item                 IPM        IPM        Machines        Machine              Heat Cost
---------------------------------------------------------------------------------------------------
calcium powder               60      40.00       0.67 ( 1) furnace                 8    200 bbm
glass                        20      20.00       1.00 ( 1) furnace                 8    200 bbm
helium-3                    240      20.00       0.08 ( 1) helium-3 extractor     60    250 bbm

┌────────────────────────────────────────────────┐
│ furnace (x1)  [heat 8] [200 bbm]               │
│ glass                                          │
│ prov: 20    (20/machine)                       │
│ req:  20.00 (1.000 machines)                   │
└────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ furnace (x1)  [heat 8] [200 bbm]               │
|   │ calcium powder                                 │
|   │ prov: 60    (60/machine)                       │
|   │ req:  40.00 (0.667 machines)                   │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ INPUT                                          │
|   |   │ calcium block                                  │
|   |   │ prov: 100                                      │
|   |   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ helium-3 extractor (x1)  [heat 60] [250 bbm]   │
|   │ helium-3                                       │
|   │ prov: 240    (240/machine)                     │
|   │ req:  20.00 (0.083 machines)                   │
|   └────────────────────────────────────────────────┘
```

The provided input is shown in the tree as a special block with machine name
"INPUT". This block only has three lines:
1. INPUT
2. Provided item name
3. Number of items provided per minute
```
┌────────────────────────────────────────────────┐
│ INPUT                                          │
│ calcium block                                  │
│ prov: 100                                      │
└────────────────────────────────────────────────┘
```

#### Example with multiple inputs
The order of inputs in the JSON file is not relevant.
```sh
python3 srcalc.py --spec ceramics.json
```
```json
{
    "request": {
        "item": "ceramics",
        "items_per_minute": 120
    },
    "inputs":[
      {
        "for_item":["ceramics", "wolfram powder"],
        "provided_item": "wolfram bar",
        "provided_ipm": 20
      },
      {
        "for_item":["ceramics"],
        "provided_item": "calcite sheets",
        "provided_ipm": 77
      }
    ]
}
```
```
╔═════════════════════════════════╗
║                                 ║
║ REQUESTING: 120 ipm of ceramics ║
║                                 ║
╚═════════════════════════════════╝

                     Provided   Required   Num
Item                 IPM        IPM        Machines        Machine              Heat Cost
---------------------------------------------------------------------------------------------------
ceramics                    120     120.00       2.00 ( 2) furnace                16    400 bbm
wolfram powder               90      60.00       0.67 ( 1) furnace                 8    200 bbm

┌────────────────────────────────────────────────┐
│ furnace (x2)  [heat 16] [400 bbm]              │
│ ceramics                                       │
│ prov: 120    (60/machine)                      │
│ req:  120.00 (2.000 machines)                  │
└────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ INPUT                                          │
|   │ calcite sheets                                 │
|   │ prov: 77                                       │
|   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ furnace (x1)  [heat 8] [200 bbm]               │
|   │ wolfram powder                                 │
|   │ prov: 90    (90/machine)                       │
|   │ req:  60.00 (0.667 machines)                   │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ INPUT                                          │
|   |   │ wolfram bar                                    │
|   |   │ prov: 20                                       │
|   |   └────────────────────────────────────────────────┘
```

### Using a specification file with existing inputs that are insufficient to cover input requirements
If the existing manufacturing capacity is insufficient to cover all the needs of a machine in the
production chain, the amount above what is provided by the existing input is calculated.

In this specification file, the provided 20 "calcite sheets" per minute is below the required
rate of 60. The calculation will then proceed to add a production chain for the remaining
40 IPM.
```json
{
    "request": {
        "item": "ceramics",
        "items_per_minute": 120
    },
    "inputs":[
      {
        "for_item":["ceramics", "wolfram powder"],
        "provided_item": "wolfram bar",
        "provided_ipm": 20
      },
      {
        "for_item":["ceramics"],
        "provided_item": "calcite sheets",
        "provided_ipm": 20
      }
    ]
}
```

The tree output includes the provided INPUT for "calcite sheets" as well as the calculated input
for the additional 40 IPM.
```
╔═════════════════════════════════╗
║                                 ║
║ REQUESTING: 120 ipm of ceramics ║
║                                 ║
╚═════════════════════════════════╝

                     Provided   Required   Num
Item                 IPM        IPM        Machines        Machine              Heat Cost
---------------------------------------------------------------------------------------------------
calcite sheets               60      40.00       0.67 ( 1) fabricator              5    140 bbm
calcium block                60      20.00       0.33 ( 1) smelter                 3    100 bbm
calcium ore                 120      20.00       0.17 ( 1) ore excavator           3     80 bbm
ceramics                    120     120.00       2.00 ( 2) furnace                16    400 bbm
wolfram powder               90      60.00       0.67 ( 1) furnace                 8    200 bbm

┌────────────────────────────────────────────────┐
│ furnace (x2)  [heat 16] [400 bbm]              │
│ ceramics                                       │
│ prov: 120    (60/machine)                      │
│ req:  120.00 (2.000 machines)                  │
└────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ INPUT                                          │
|   │ calcite sheets                                 │
|   │ prov: 20                                       │
|   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ fabricator (x1)  [heat 5] [140 bbm]            │
|   │ calcite sheets                                 │
|   │ prov: 60    (60/machine)                       │
|   │ req:  40.00 (0.667 machines)                   │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ smelter (x1)  [heat 3] [100 bbm]               │
|   |   │ calcium block                                  │
|   |   │ prov: 60    (60/machine)                       │
|   |   │ req:  20.00 (0.333 machines)                   │
|   |   └────────────────────────────────────────────────┘
|   |   |   ┌────────────────────────────────────────────────┐
|   |   |   │ ore excavator (x1)  [heat 3] [80 bbm]          │
|   |   |   │ calcium ore                                    │
|   |   |   │ prov: 120    (120/machine)                     │
|   |   |   │ req:  20.00 (0.167 machines)                   │
|   |   |   └────────────────────────────────────────────────┘
|   ┌────────────────────────────────────────────────┐
|   │ furnace (x1)  [heat 8] [200 bbm]               │
|   │ wolfram powder                                 │
|   │ prov: 90    (90/machine)                       │
|   │ req:  60.00 (0.667 machines)                   │
|   └────────────────────────────────────────────────┘
|   |   ┌────────────────────────────────────────────────┐
|   |   │ INPUT                                          │
|   |   │ wolfram bar                                    │
|   |   │ prov: 20                                       │
|   |   └────────────────────────────────────────────────┘
```

## Items and buildings data

The program reads 4 files to build it's item database:
| File | Description |
|------|-------------|
| starrupture_recipe_items.csv | Master list of items that defines the name, the machine used to craft, and the rate that the machine is capable of outputting. |
| starrupture_recipe_input.csv | Links the inputs required for crafting an item, to the item, as well as the consumption rate. |
| starrupture_recipe_raw.csv | Master list of special items that are not crafted but are the starting inputs into the production chain. |
| starrupture_recipe_buildings.csv | Master list of buildings that defines the costs. |

### starrupture_recipes.ods

There is an additional file in the code repo which is not used by the program but is the mechanism
I use to produce the data files. File "starrupture_recipes.ods" is a LibreOffice Calc file with a
sheet for each data file. The sheets include some simple formula to populate some rate columns.
To modify the item data, you don't need to use this file as the *.csv files can be edited directly.

#### Adding an item to the sheet
To add an item, in the next available row of sheet "Items", enter the name into the _Item_ column,
the amount crafted as specified by the recipe in _NumProduced_, and the number of seconds per item
in _PeriodSeconds_. The name of the machine is entered into column _Factory_ and finally the formula
in _ItemsPerMinute_ is copied from an existing row.

| Column | Data |
|--------|------|
| Item | Item name as specified by the recipe. |
| NumProduced | The amount crafted as specified by the recipe. |
| PeriodSeconds | The number of seconds per item as specified by the recipe. |
| Factory | The name of the machine crafting the item. |
| ItemsPerMinute | Formula copied from an existing row. |

* The names must be lowercase.
* The machine must exist in sheet "buildings". If not, capture the building details first.
* The sheet must be sorted on column _Item_.

#### Adding the item inputs to the sheet
After adding the item to sheet "Items", switch to sheet "Input" and add a row for each input required
to craft the item. The item name as entered in sheet "Items" must be entered into the column _Item_.
The item name for the input is entered into column _Input_. The amount of items for that input, as
specified by the recipe, is entered into _NumRequired_. The columns _PeriodSeconds_ and
_RequiredPerMinute_ are formulas that are copied from an existing row.

| Column | Data |
|--------|------|
| Item | Name of item being crafted. |
| Input | Name of an item required as input to the recipe. |
| NumRequired | The input item amount as specified by the recipe.  |
| PeriodSeconds | Formula copied from an existing row. |
| RequiredPerMinute | Formula copied from an existing row. |

* The names must be lowercase.
* The formula in _PeriodSeconds_ is a VLOOKUP that searches the "Items" sheet up to row 50.
  If you have added rows beyond 50 in sheet "Items", you will have to update the formula.
* The sheet must be sorted on columns _Item_ and _Input_.


#### Adding a raw item to the sheet
The raw item is added for each variant. If the raw item doesn't have variants, then the _Variant_
column is set to "normal".

| Column | Data |
|--------|------|
| Item | Ore / gas item name as specified by the recipe. |
| Variant | From the recipe when named: either "impure" or "pure". When the recipe omits the name, then "normal". |
| NumProduced | The amount produced as specified by the recipe. |
| PeriodSeconds | The time, in seconds, to produce items as specified by the recipe. |
| Factory | The name of the building extracting the item.  |
| ItemsPerMinute | Formula copied from an existing row. |

* The names must be lowercase.
* The building entered into _Factory_ must exist in sheet "buildings". If not, capture the building
  details first.
* The sheet must be sorted on columns _Item_ and _Variant_.

#### Adding a building to the sheet

| Column | Data |
|--------|------|
| building | Name of machine or building. |
| heat | The amount of heat added, or removed by constructing the building. Negative numbers represent buildings that remove heat. |
| bbm cost | Basic building material cost. The cell must only be populated if the cost requires basic building materials. |
| ibm cost | Intermediate building material cost. The cell must only be populated if the cost requires intermediate building materials. |
| qbm cost | Quartz building material cost. The cell must only be populated if the cost requires quartz building materials. |

* The names must be lowercase.
* The sheet must be sorted on column _building_.

#### Creating the CSV files from the sheet

Each CSV file is written by selecting the sheet to write, then using menu option "File" -> "Save a Copy...".

* Sheet Items is written to "starrupture_recipe_items.csv"
* Sheet Input is written to "starrupture_recipe_input.csv"
* Sheet raw is written to "starrupture_recipe_raw.csv"
* Sheet building is written to "starrupture_recipe_buildings.csv"
* File format must be changed to "Text CSV (.csv)"
* Character set is UTF-8.
* The Field delimiter must be a semicolon ;
* String delimiter is double quotes "
* Option "Save cell contents as shown" must be the only one enabled.

### Adding an item directly to the CSV files

If you wish to add an item without using "starrupture_recipes.ods", then the process is almost
identical to the one outlined for adding to the sheet except that the calculations must be performed
manually.

* Character set is UTF-8.
* The Field delimiter must be a semicolon ;

#### Adding an item to file "starrupture_recipe_items.csv"
Follow the instruction as per [adding the item to the sheet "Item"](#adding-an-item-to-the-sheet) for each column except:
* The item must be inserted into the row which retains item name alphabetic order.
* Column _ItemsPerMinute_ is calculated using formula: 60/_PeriodSeconds_*_NumProduced_

#### Adding an item to file "starrupture_recipe_input.csv"
Follow the instruction as per [adding the item inputs to the sheet "Input"](#adding-the-item-inputs-to-the-sheet) for each column except:
* The item must be inserted into the row which retains item name and input name alphabetic order.
* Column _PeriodSeconds_ is copied from "starrupture_recipe_items.csv" column _PeriodSeconds_
  for the crafted item.
* Column _RequiredPerMinute_ is calculated using formula 60/_PeriodSeconds_*_NumRequired_

#### Adding an item to file "starrupture_recipe_raw.csv"
Follow the instruction as per [adding the item inputs to the sheet "raw"](#adding-a-raw-item-to-the-sheet) for each column except:
* The item must be inserted into the row which retains item name and variant alphabetic order.
* Column _ItemsPerMinute_ is calculated using formula: 60/_PeriodSeconds_*_NumProduced_

#### Adding an item to file "starrupture_recipe_buildings.csv"
Follow the instruction as per [adding the item inputs to the sheet "buildings"](#adding-a-building-to-the-sheet) for each column
except:
* The building must be inserted into the row which retains building name alphabetic order.
