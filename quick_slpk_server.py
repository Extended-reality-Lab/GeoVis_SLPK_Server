#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QUICK SLPK SERVER
======================

Minimalist web server engine to publish OGC SceneLayerPackage (.slpk) to Indexed 3d Scene Layer (I3S) web service.

How to use:
- Place .SLPK into a folder (default: "./slpk")
- Configure this script:
	- webserver host
	- webserver port
	- slpk folder
- Launch this script 
- Open browser to "host:port"
- Index page let you access your SLPK as I3S services
-  Also provide an intern viewer for test

How to:
- Configure Index page: modify->  views/services_list.tpl
- Configure Viewer page: modify->  views/carte.tpl


Sources:
- python 2.x
- I3S Specifications: https://github.com/Esri/i3s-spec
- BottlePy 0.13+
- Arcgis Javascript API >=4.6


Autor: RIVIERE Romain
Date: 12/02/2018
Licence: GNU GPLv3 

"""

# Import python modules
import bottle
from bottle import app, route, run, template, abort, response
from io import BytesIO
import os, sys, json, gzip, zipfile

# User parameter
host = 'localhost'
port = 8083
home = os.path.join(os.path.dirname(os.path.realpath(__file__)), "slpk")  # SLPK Folder

# *********#
# Functions#
# *********#

# List available SLPK
sceneFiles = [f for f in os.listdir(home) if os.path.splitext(f)[1].lower() == u".slpk"]


def read(f, slpk):
    """read gz compressed file from slpk (=zip archive) and output result"""
    if f.startswith("\\"):  # remove first \
        f = f[1:]
    with open(os.path.join(home, slpk), 'rb') as file:
        with zipfile.ZipFile(file) as zip:
            if os.path.splitext(f)[1] == ".gz":  # unzip GZ
                gz = BytesIO(zip.read(f.replace("\\", "/")))  # GZ file  -> convert path sep to zip path sep
                with gzip.GzipFile(fileobj=gz) as gzfile:
                    return gzfile.read()
            else:
                return zip.read(f.replace("\\", "/"))  # Direct read


# the decorator
def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers[
            'Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors


# *********#
# SRIPT****#
# *********#

app = app()


@app.route('/')
def list_services():
    """ List all available SLPK, with LINK to I3S service and Viewer page"""
    return template('services_list', slpks=sceneFiles)


@app.route('/<slpk>/FeatureServer')
@app.route('/<slpk>/FeatureServer/')
@enable_cors
def feature_server_info(slpk):
    # Not available
    return json.dumps([])




@app.route('/<slpk>/SceneServer')
@app.route('/<slpk>/SceneServer/')
@enable_cors
def service_info(slpk):
    """ Service information JSON """
    if slpk not in sceneFiles:  # Get 404 if slpk doesn't exists
        abort(404, f"Can't found SLPK: {slpk}")
    SceneServiceInfo = dict()
    SceneServiceInfo["serviceName"] = slpk
    SceneServiceInfo["name"] = slpk
    SceneServiceInfo["currentVersion"] = 10.6
    SceneServiceInfo["serviceVersion"] = "1.6"
    SceneServiceInfo["supportedBindings"] = ["REST"]
    SceneServiceInfo["layers"] = [json.loads(read("3dSceneLayer.json.gz", slpk))]
    response.content_type = 'application/json'
    return json.dumps(SceneServiceInfo)


@app.route('/<slpk>/SceneServer/layers/0')
@app.route('/<slpk>/SceneServer/layers/0/')
@enable_cors
def layer_info(slpk):
    """ Layer information JSON """
    if slpk not in sceneFiles:  # Get 404 if slpk doesn't exists
        abort(404, f"Can't found SLPK: {slpk}")
    SceneLayerInfo = json.loads(read("3dSceneLayer.json.gz", slpk))
    response.content_type = 'application/json'
    return json.dumps(SceneLayerInfo)

@app.route('/<slpk>/SceneServer/layers/<layer>/nodepages')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodepages/')
@enable_cors
def node_info(slpk, layer):
    """ Node information JSON """
    if slpk not in sceneFiles:  # Get 404 if slpk doesn't exists
        abort(404, f"Can't found SLPK: {slpk}")
    NodeIndexDocument = json.loads(read("nodepages/0.json.gz", slpk))
    response.content_type = 'application/json'
    return json.dumps(NodeIndexDocument)

@app.route('/<slpk>/SceneServer/layers/<layer>/nodepages/<node>')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodepages/<node>/')
@enable_cors
def node_info(slpk, layer, node):
    """ Node information JSON """
    if slpk not in sceneFiles:  # Get 404 if slpk doesn't exists
        abort(404, f"Can't found SLPK: {slpk}")
    NodeIndexDocument = json.loads(read(f"nodepages/{node}.json.gz", slpk))
    response.content_type = 'application/json'
    return json.dumps(NodeIndexDocument)

@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/')
@enable_cors
def node_info(slpk, layer, node):
    """ Node information JSON """
    if slpk not in sceneFiles:  # Get 404 if slpk doesn't exists
        abort(404, f"Can't found SLPK: {slpk}")
    NodeIndexDocument = json.loads(read(f"nodes/{node}/3dNodeIndexDocument.json.gz", slpk))
    response.content_type = 'application/json'
    return json.dumps(NodeIndexDocument)


@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/geometries/0')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/geometries/0/')
@enable_cors
def geometry_info(slpk, layer, node):
    """ Geometry information bin """
    if slpk not in sceneFiles:  # Get 404 if slpk doesn't exists
        abort(404, f"Can't found SLPK: {slpk}")
    response.content_type = 'application/octet-stream; charset=binary'
    response.content_encoding = 'gzip'
    return read(f"nodes/{node}/geometries/0.bin.gz", slpk)


@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/textures/0_0')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/textures/0_0/')
@enable_cors
def textures_info(slpk, layer, node):
    """ Texture information JPG """
    if slpk not in sceneFiles:  # Get 404 if slpk doesn't exists
        abort(404, f"Can't found SLPK: {slpk}")

    response.headers['Content-Disposition'] = 'attachment; filename="0_0.jpg"'
    response.content_type = 'image/jpeg'
    try:
        return read(f"nodes/{node}/textures/0_0.jpg", slpk)
    except:
        try:
            return read(f"nodes/{node}/textures/0_0.bin", slpk)
        except:
            return ""

@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/textures/<texture>')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/textures/<texture>/')
@enable_cors
def textures_info(slpk, layer, node, texture):
    """ Texture information JPG """
    if slpk not in sceneFiles:  # Get 404 if slpk doesn't exists
        abort(404, f"Can't found SLPK: {slpk}")

    response.headers['Content-Disposition'] = f'attachment; filename="{texture}.jpg"'
    response.content_type = 'image/jpeg'
    try:
        return read(f"nodes/{node}/textures/{texture}.jpg", slpk)
    except:
        try:
            return read(f"nodes/{node}/textures/{texture}.bin", slpk)
        except:
            return ""

@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/textures/0_0_1')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/textures/0_0_1/')
@enable_cors
def Ctextures_info(slpk, layer, node):
    """ Compressed texture information """
    if slpk not in sceneFiles:  # Get 404 if slpk doesn't exists
        abort(404, f"Can't found SLPK: {slpk}")
    try:
        return read(f"nodes/{node}/textures/0_0_1.bin.dds.gz", slpk)
    except:
        return ""


@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/features/0')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/features/0/')
@enable_cors
def feature_info(slpk, layer, node):
    """ Feature information JSON """
    if slpk not in sceneFiles:  # Get 404 if slpk doesn't exists
        abort(404, f"Can't found SLPK: {slpk}")
    FeatureData = json.loads(read(f"nodes/{node}/features/0.json.gz", slpk))
    response.content_type = 'application/json'
    return json.dumps(FeatureData)


@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/shared')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/shared/')
@enable_cors
def shared_info(slpk, layer, node):
    """ Shared node information JSON """
    if slpk not in sceneFiles:  # Get 404 if slpk doesn't exists
        abort(404, f"Can't found SLPK: {slpk}")
    try:
        Sharedressource = json.loads(read(f"nodes/{node}/shared/sharedResource.json.gz", slpk))
        response.content_type = 'application/json'
        return json.dumps(Sharedressource)
    except:
        return ""


@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/attributes/<attribute>/0')
@app.route('/<slpk>/SceneServer/layers/<layer>/nodes/<node>/attributes/<attribute>/0/')
@enable_cors
def attribute_info(slpk, layer, node, attribute):
    """ Attribute information JSON """
    if slpk not in sceneFiles:  # Get 404 if slpk doesn't exists
        abort(404, f"Can't found SLPK: {slpk}")
    return read(f"nodes/{node}/attributes/{attribute}/0.bin.gz", slpk)


@app.route('/carte/<slpk>')
@enable_cors
def carte(slpk):
    """ Preview data on a 3d globe """
    if slpk not in sceneFiles:  # Get 404 if slpk doesn't exists
        abort(404, f"Can't found SLPK: {slpk}")
    return template('carte', slpk=slpk, url=f"http://{host}:{port}/{slpk}/SceneServer/layers/0")


@app.route('/reload')
@enable_cors
def reload():
    global sceneFiles
    sceneFiles = [f for f in os.listdir(home) if os.path.splitext(f)[1].lower() == u".slpk"]


# Run server
app.run(host=host, port=port)
