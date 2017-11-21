from rest_framework.routers import SimpleRouter, Route, DynamicListRoute


class SingleRecordRouter(SimpleRouter):
    routes = [
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'post': 'create',
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]
