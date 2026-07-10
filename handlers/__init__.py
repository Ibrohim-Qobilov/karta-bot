"""Barcha routerlar. Dispatcherga shu tartibda ulanadi.

`interrupt` eng birinchi turadi: menyu tugmalari istalgan FSM holati ichida ham
ishlashi va oqimni bekor qilishi uchun.
"""
from . import interrupt, start, cards, edit, settings, backup, inline

routers = (
    interrupt.router,
    start.router,
    cards.router,
    edit.router,
    settings.router,
    backup.router,
    inline.router,
)
