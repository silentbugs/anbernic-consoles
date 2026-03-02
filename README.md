## 1. Compare ROMs

```bash
silentz0r@Aegon ~/Downloads/media/games % poetry run python compare_roms.py ../gamelist.json \
    /Volumes/Public/Installers/Games/Emulators/ROMs \
    /Volumes/Public/Installers/Games/Emulators/AnbernicSD
```

## 2. Collect ROMs

```bash
poetry run python collect_roms.py ../gamelist.json \
    /Volumes/Public/Installers/Games/Emulators/ROMs \
    /Volumes/Public/Installers/Games/Emulators/AnbernicSD \
    --dest ~/tmp/roms/ \
    --dry-run
```

```bash
poetry run python collect_roms.py ../gamelist.json \
    /Volumes/Public/Installers/Games/Emulators/ROMs \
    /Volumes/Public/Installers/Games/Emulators/AnbernicSD \
    --dest ~/tmp/roms/ \
    --exclude-system PS2 \
    --exclude-system PSP \
    --exclude-system PSX \
    --exclude-system GC \
    --exclude-system DREAMCAST \
    --dry-run
```

# Console setup

Refer to [Console Setup.MD](./console_setup.md) in order to prepare a console.

