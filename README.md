# StarRupture Production Calculator

A python 3 program that can be used to determine what inputs, and machines are necessary to craft a specific item with a specific rate.
The output of the program is a summary of required items as well as a production tree starting with the requested item and working backwards 
to the raw materials that start the chain.

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

### Summary section of output
The summary table provides the total requirements for each item in alphabetical order.
| Column | Description |
|--------|-------------|
| Item | Name of item |
| Provided IPM | The rate, in items per minute, that is output by all the machines crafting that item. |
| Required IPM | The rate, in items per minute, that the item is consumed by the production chain. |
| Num Machines | The number of machines that are required to satisfy the required IPM. The value in parenthesis is the amount rounded to the next whole number. |
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

