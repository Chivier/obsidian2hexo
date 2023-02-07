# H2O2H

This repository is used to help Obsidian publish more conveniently.

## Installing

```bash
pip install o2h
```

## Getting Started

After o2h package is installed, the cli command obs2hexo is available. The help info is listed here.

```bash
obs2hexo -h

usage: obs2hexo [-h] [-o OUTPUT] [-c CATEGORY] [-p | --picgo | --no-picgo] filename

positional arguments:
  filename              get the obs markdown filename

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        get output dir
  -c CATEGORY, --category CATEGORY
                        get category
  -p, --picgo, --no-picgo
                        use picgo
```

As the Github repository space is limited, so it is not recommanded to upload all the pictures  to the repository. So I provide an alternative option `-p` to upload pictures with [picgo](https://github.com/PicGo/PicGo-Core).

The default output directory is `/tmp/o2houtput`.

## Configuration

o2h cannot find the position of Obsidian Vault automatically, so it relies on the configuration file. A configuration file should be created in `$HOME/.config/o2h/config.json`

Here is an example of my config file:

```json
{
    "obsidian_target": [
        "$HOME/Documents/Work/Notes"
    ]
}
```

If there are multiple Obsidian Vault in you system, you can add them like this:

```json
{
  "obsidian_target": [
    "path_1",
    "path_2",
    ...,
    "path_n"
  ]
}
```

## Example

Here are some examples:

```bash
# translate a.md to standard markdown
# the category is "Skill"
# all the picture are copied to a new folder named 'a' in current directory
obs2hexo -o $PWD -c Skill a.md
# translate b.md to /tmp/o2houtput, all the picture are uploaded by picgo
obs2hexo -c Develop -p b.md
```
