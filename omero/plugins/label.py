# encoding: utf-8
#
# Copyright (c) 2025 Glencoe Software, Inc. All rights reserved.
#
# This software is distributed under the terms described by the LICENCE file
# you can find at the root of the distribution bundle.
# If the file is missing please request a copy by contacting
# support@glencoesoftware.com.


import sys

from omero.cli import BaseControl
from omero.cli import CLI
from omero.model import ExternalInfoI
from omero.rtypes import unwrap

from omero_label import create_label, create_external_info, \
                        query_pixels, query_mask


HELP = """Register and manage OME-Zarr labels

Examples:

    $ omero label register /data/image.zarr/0/labels/cells 1
    Roi:5358
    $ omero label get 5358
    x=0.0
    y=0.0
    width=1584.0
    height=788.0
    fillColor=-65436
    uri=/data/image.zarr/0/labels/cells
    name=label
    $ omero label get 5358 uri
    /data/image.zarr/0/labels/cells
    $ omero label update 5358 /data/image.zarr/0/labels/cells_new
"""

NGFF_ENTITY_TYPE = 'com.glencoesoftware.ngff:multiscales'
NGFF_ENTITY_ID = 3


class LabelControl(BaseControl):

    def _configure(self, parser):
        parser.add_login_arguments()
        sub = parser.sub()

        register = parser.add(
            sub, self.register, help="Register an OME-Zarr label")
        register.add_argument(
            "uri", type=str, help="URI to the OME-Zarr label")
        register.add_argument(
            "image_id", type=int,
            help="ID of the image to associate the label with")
        register.add_argument(
            "--name", type=str, default="label", help="Label name")

        get = parser.add(
            sub, self.get, help="Retrieve the label properties")
        get.add_argument(
            "label_id", type=int,
            help="ID of the ROI object associated with the label")
        get.add_argument(
            "property", type=str, nargs="?",
            help="Label property to retrieve")

        update = parser.add(
            sub, self.update, help="Update a label uri")
        update.add_argument(
            "label_id", type=int,
            help="ID of the ROI object associated with the label")
        update.add_argument(
            "uri", type=str, help="New URI to the OME-Zarr label")

    def register(self, args):
        client = self.ctx.conn(args)
        session = client.getSession()

        pixels = query_pixels(session, args.image_id)
        if pixels is None:
            self.ctx.die(334, f"No image {args.image_id} found")

        roi = create_label(
            args.name, args.uri, pixels.sizeX.val, pixels.sizeY.val,
            args.image_id)

        roi = session.getUpdateService().saveAndReturnObject(
            roi, {"omero.group": str(pixels.details.group.id.val)})
        self.ctx.out(f"Roi:{roi.id.val}")

    def update(self, args):
        client = self.ctx.conn(args)
        session = client.getSession()
        mask = query_mask(session, args.label_id)
        if mask is None:
            self.ctx.die(334, f"No ROI {args.roi_id} found")

        old_externalInfo = mask.details.externalInfo
        mask.details.externalInfo = create_external_info(
            args.uri,
            NGFF_ENTITY_TYPE,
            NGFF_ENTITY_ID)

        session.getUpdateService().saveObject(
            mask, {"omero.group": str(mask.details.group.id.val)})
        session.getUpdateService().deleteObject(
            ExternalInfoI(old_externalInfo.id.val, False))

    def get(self, args):
        client = self.ctx.conn(args)
        session = client.getSession()
        mask = query_mask(session, args.label_id)
        if mask is None:
            self.ctx.die(334, f"No ROI {args.roi_id} found")

        properties = {
            "x": unwrap(mask.x),
            "y": unwrap(mask.x),
            "width": unwrap(mask.width),
            "height": unwrap(mask.height),
            "fillColor": unwrap(mask.fillColor),
            "uri": unwrap(mask.details.externalInfo.lsid),
            "name": unwrap(mask.textValue),
        }
        if args.property is not None:
            self.ctx.out(f"{properties[args.property]}")
        else:
            for k, v in properties.items():
                self.ctx.out(f"{k}={v}")


try:
    register("label", LabelControl, HELP)
except NameError:
    if __name__ == "__main__":
        cli = CLI()
        cli.register("label", LabelControl, HELP)
        cli.invoke(sys.argv[1:])
