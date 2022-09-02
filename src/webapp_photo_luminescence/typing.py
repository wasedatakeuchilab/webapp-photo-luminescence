import typing as t

from dash.development import base_component

Child = t.Union[base_component.Component, str, int]
Children = t.Union[list[Child], Child, None]
