# omero-label

Python library and OMERO CLI plugin to manage OME-Zarr labels in OMERO.

[OME-Zarr](https://ngff.openmicroscopy.org/specifications/index.html) groups containing
label images can be linked to individual OMERO images as ROIs containing a single Mask
shape as defined in the
[omero-zarr-pixel-buffer](https://github.com/glencoesoftware/omero-zarr-pixel-buffer/blob/master/README.md#usage)
extension.

## Requirements

* Python 3.10 or later

## Installation

`omero-label` is distributed via PyPI and can be installed using the standard
Python packaging managers like `pip`:

    pip install omero-label

## Usage

To register an OME-Zarr label, run the `omero label register` using the absolute
path to the label group and the ID of the image to link the label to:

    omero label register /path/to/image.zarr/0/labels/my_label <image_id>

A successful registration will return the ID of the new object as `Roi:<roi_id>`.

The properties of a label image can be retrieved by calling the `omero label get` command
using the ID of the ROI:

    omero label get <roi_id>

The command will return the properties as a list of key/value pairs:

    x=0.0
    y=0.0
    width=1584.0
    height=788.0
    fillColor=-65436
    uri=/data/image.zarr/0/labels/cells

Properties can also be retrieved individually by specifying their name as an
argument:

    omero label get <roi_id> x
    omero label get <roi_id> width
    omero label get <roi_id> fillColor

To update the location of an OME-Zarr label, run `omero label update`:

    omero label update <roi_id> /new/path/to/image.zarr/0/labels/my_label

## Development

Clone the repository:

    git clone https://github.com/glencoesoftware/omero-label

Build the project using the build module:

    pip intall build
    python -m build

## License

omero-label is licensed under the terms of the GNU General Public License (GPL) v2.
