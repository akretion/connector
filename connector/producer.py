# -*- coding: utf-8 -*-
# Copyright 2013-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Producers of events.

Fire the common events:

-  ``on_record_create`` when a record is created
-  ``on_record_write`` when something is written on a record
-  ``on_record_unlink``  when a record is deleted

"""

import openerp
from openerp import models
from .event import (on_record_create,
                    on_record_write,
                    on_record_unlink)
from .connector import is_module_installed


create_original = models.BaseModel.create


@openerp.api.model
@openerp.api.returns('self', lambda value: value.id)
def create(self, vals):
    record_id = create_original(self, vals)
    if is_module_installed(self.env, 'connector'):
        on_record_create.fire(self.env, self._name, record_id.id, vals)
    return record_id


models.BaseModel.create = create


write_original = models.BaseModel.write


@openerp.api.multi
def write(self, vals):
    result = write_original(self, vals)
    if is_module_installed(self.env, 'connector'):
        if on_record_write.has_consumer_for(self.env, self._name):
            for record_id in self.ids:
                on_record_write.fire(self.env, self._name,
                                     record_id, vals)
    return result


models.BaseModel.write = write


unlink_original = models.BaseModel.unlink


@openerp.api.multi
def unlink(self):
    if is_module_installed(self.env, 'connector'):
        if on_record_unlink.has_consumer_for(self.env, self._name):
            for record_id in self.ids:
                on_record_unlink.fire(self.env, self._name, record_id)
    return unlink_original(self)


models.BaseModel.unlink = unlink
