#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Glencoe Software, Inc.  All rights reserved.
#
# This software is distributed under the terms described by the LICENCE.txt
# file you can find at the root of the distribution bundle.  If the file is
# missing please request a copy by contacting info@glencoesoftware.com.

import logging
import omero
import omero.clients

from omero.rtypes import rdouble, rint, rlong, rstring
from omero.model import ExternalInfoI
from omero.model import ImageI
from omero.model import MaskI
from omero.model import RoiI

LOGGER = logging.getLogger(__name__)

NGFF_LABEL_ENTITY_TYPE = "com.glencoesoftware.ngff:multiscales"
NGFF_LABEL_ENTITY_ID = 3


def create_label(name, uri, width, height, image_id):
    roi = RoiI()
    roi.setName(rstring(name))
    mask = create_mask(0, 0, width, height, name)
    mask.details.externalInfo = create_external_info(
        uri, NGFF_LABEL_ENTITY_TYPE, NGFF_LABEL_ENTITY_ID)
    roi.addShape(mask)
    roi.setImage(ImageI(image_id, False))
    return roi


def create_mask(x, y, width, height, text_value, color=[255, 255, 0, 100]):
    mask = MaskI()
    mask.setX(rdouble(x))
    mask.setY(rdouble(y))
    mask.setWidth(rdouble(width))
    mask.setHeight(rdouble(height))
    mask.setTextValue(rstring(text_value))
    fill_color = int.from_bytes(color, byteorder="big", signed=True)
    mask.setFillColor(rint(fill_color))
    return mask


def create_external_info(uri, entity_type, entity_id):
    externalInfo = ExternalInfoI()
    externalInfo.entityType = rstring(entity_type)
    externalInfo.entityId = rlong(entity_id)
    externalInfo.lsid = rstring(uri)
    return externalInfo


def query_pixels(conn, image_id):
    params = omero.sys.ParametersI()
    params.addId(image_id)
    query = "select p from Pixels p where p.image.id = :id"
    return conn.getQueryService().findByQuery(
        query, params, {"omero.group": "-1"})


def query_mask(conn, roi_id):
    params = omero.sys.ParametersI()
    params.addId(roi_id)
    query = (
        "select m from Mask m "
        "join fetch m.details.externalInfo "
        "where m.roi.id = :id")
    return conn.getQueryService().findByQuery(
        query, params, {"omero.group": "-1"})
