#!/usr/bin/env python
#coding:utf-8
# Author:  mozman --<mozman@gmx.at>
# Purpose: filters module
# Created: 03.11.2010
# Copyright (C) 2010, Manfred Moitzi
# License: GPLv3

from base import BaseElement
from interface import IXLink
from mixins import Presentation
from utils import strlist

class _FilterPrimitive(BaseElement, Presentation):
    pass

class _FilterNoInput(_FilterPrimitive):
    def __init__(self, start=None, size=None, **extra):
        super(_FilterNoInput, self).__init__(**extra)
        if start is not None:
            self['x'] = start[0]
            self['y'] = start[1]
        if size is not None:
            self['width'] = size[0]
            self['height'] = size[1]

class _FilterRequireInput(_FilterNoInput):
    def __init__(self, in_, **extra):
        super(_FilterRequireInput, self).__init__(**extra)
        self['in'] = in_

class _feBlend(_FilterRequireInput):
    elementname = 'feBlend'

class _feColorMatrix(_FilterRequireInput):
    elementname = 'feColorMatrix'

class _feComponentTransfer(_FilterRequireInput):
    elementname = 'feComponentTransfer'
    def feFuncR(self, type_, **extra):
        return self.add(_feFuncR(type_, factory=self, **extra))
    def feFuncG(self, type_, **extra):
        return self.add(_feFuncG(type_, factory=self, **extra))
    def feFuncB(self, type_, **extra):
        return self.add(_feFuncB(type_, factory=self, **extra))
    def feFuncA(self, type_, **extra):
        return self.add(_feFuncA(type_, factory=self, **extra))

class _feFuncR(_FilterPrimitive):
    elementname = 'feFuncR'
    def __init__(self, type_, **extra):
        super(_feFuncR, self).__init__(**extra)
        self['type'] = type_

class _feFuncG(_feFuncR):
    elementname = 'feFuncG'

class _feFuncB(_feFuncR):
    elementname = 'feFuncB'

class _feFuncA(_feFuncR):
    elementname = 'feFuncA'

class _feComposite(_FilterRequireInput):
    elementname = 'feComposite'

class _feConvolveMatrix(_FilterRequireInput):
    elementname = 'feConvolveMatrix'

class _feDiffuseLighting(_FilterRequireInput):
    elementname = 'feDiffuseLighting'

class _feDisplacementMap(_FilterRequireInput):
    elementname = 'feDisplacementMap'

class _feFlood(_FilterNoInput):
    elementname = 'feFlood'

class _feGaussianBlur(_FilterRequireInput):
    elementname = 'feGaussianBlur'

class _feImage(_FilterNoInput, IXLink):
    elementname = 'feImage'
    def __init__(self, href, start=None, size=None, **extra):
        super(_feImage, self).__init__(start, size, **extra)
        self.set_href(href)

class _feMergeNode(_FilterPrimitive):
    elementname = 'feMergeNode'

class _feMerge(_FilterNoInput):
    elementname = 'feMerge'
    def __init__(self, layernames, **extra):
        super(_feMerge, self).__init__(**extra)
        self.feMergeNode(layernames)

    def feMergeNode(self, layernames):
        for layername in layernames:
            self.add(_feMergeNode(in_=layername, factory=self))

class _feMorphology(_FilterRequireInput):
    elementname = 'feMorphology'

class _feOffset(_FilterRequireInput):
    elementname = 'feOffset'

class _feSpecularLighting(_FilterRequireInput):
    elementname = 'feSpecularLighting'

class _feTile(_FilterRequireInput):
    elementname = 'feTile'

class _feTurbulence(_FilterNoInput):
    elementname = 'feTurbulence'

filter_factory = {
    'feBlend': _feBlend,
    'feColorMatrix': _feColorMatrix,
    'feComponentTransfer': _feComponentTransfer,
    'feComposite': _feComposite,
    'feConvolveMatrix': _feConvolveMatrix,
    'feDiffuseLighting': _feDiffuseLighting,
    'feDisplacementMap': _feDisplacementMap,
    'feFlood': _feFlood,
    'feGaussianBlur': _feGaussianBlur,
    'feImage': _feImage,
    'feMerge': _feMerge,
    'feMorphology': _feMorphology,
    'feOffset': _feOffset,
    'feSpecularLighting': _feSpecularLighting,
    'feTile': _feTile,
    'feTurbulence': _feTurbulence,
}

class _FilterBuilder(object):
    def __init__(self, cls, parent):
        self.cls = cls # primitive filter class to build
        self.parent = parent # the parent Filter() object

    def __call__(self, *args, **kwargs):
        kwargs['factory'] = self.parent # to get the _paramters object
        obj = self.cls(*args, **kwargs) # create an object of type 'cls'
        self.parent.add(obj) # add primitive filter to parent Filter()
        return obj

class Filter(BaseElement, IXLink, Presentation):
    elementname = 'filter'
    def __init__(self, start=None, size=None, resolution=None, inherit=None, **extra):
        super(Filter, self).__init__(**extra)
        if start is not None:
            self['x'] = start[0]
            self['y'] = start[1]
        if size is not None:
            self['width'] = size[0]
            self['height'] = size[1]
        if resolution is not None:
            if isinstance(resolution, basestring):
                self['filterRes'] = resolution
            elif hasattr(resolution, '__iter__'):
                self['filterRes'] = strlist(resolution, ' ')
            else:
                self['filterRes'] = str(resolution)

        if inherit is not None:
            self.href = inherit
            self.update_id()

    def get_xml(self):
        self.update_id()
        return super(Filter, self).get_xml()

    def __getattr__(self, name):
        # create primitive filters by Filter.<filtername>(...)
        # and auto-add the new filter as subelement of Filter()
        if name in filter_factory:
            return _FilterBuilder(filter_factory[name], self)
        else:
            raise AttributeError("'%s' has no attribute '%s'" % (self.__class__.__name__, name))
