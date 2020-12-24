# Tanki Online Patches

This is a collection of tools that aim to make patching Tanki Online client binaries more convenient.

* **disasm.py**: Fetches client binaries from Tanki Online servers and disassembles the specified scripts into a separate branch.
* **build.py**: Builds patched client from disassembled sources.
* **build_patch.py**: Builds a patch file from disassembled sources.

Tanki Online updates frequently, by using `build_patch.py` you can export your changes to a patch file, this allows effortless porting of these changes across updates. Once you're happy with your changes, run `build.py` and it will generate a patched SWF file. You can load it with the "Map Local" feature of Charles Proxy, for example.

## Requirements

`disasm.py` makes use of additional binaries that must be present in a folder named `bin`.

* [RABCDAsm](https://github.com/CyberShadow/RABCDAsm): Extract the latest release to `bin`.
* [JPEXS Free Flash Decompiler](https://github.com/jindrapetrik/jpexs-decompiler): Extract the latest release to `bin/ffdec`.

## Included patches

Patches are included in this repository that aid in reverse engineering and data mining.
Summary of a notable few:

* **entrance_pcap.patch**: Outputs ingoing and outgoing packets to the Flash debugger trace file.
* **entrance_dumpMaps.patch**: Marks all available maps as enabled and dumps them to the trace file as JSON.
Match creation details will also be dumped as JSON (BattleCreateModel).
*Note: The server will ignore any requests to create matches with maps that are disabled.*
* **entrance_bypassMigrationDialog.patch**: Stops the HTML5 migration dialog from appearing. No longer works as of 2020/12/11.
* **game_dumpMaps.patch**: Must be used in conjunction with `entrance_dumpMaps.patch`. Dumps details about maps as they are loaded in-game to the trace file as JSON (BattleMapModel).
* **game_allBuyable.patch**: Shows unobtainable items in the garage. This is a client-side only effect, they cannot actually be purchased.
