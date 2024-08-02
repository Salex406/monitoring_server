# #!/usr/bin/env python3
# from nicegui import ui

# # with ui.header().classes(replace='row items-center') as header:
# #     ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
# #     with ui.tabs() as tabs:
# #         ui.tab('A')
# #         ui.tab('B')
# #         ui.tab('C')

# # with ui.footer(value=False) as footer:
# #     ui.label('Footer')

# with ui.left_drawer().classes('bg-blue-100') as left_drawer:
#     ui.label('Side menu')

# with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
#     ui.button(on_click=footer.toggle, icon='contact_support').props('fab')

# with ui.tab_panels(tabs, value='A').classes('w-full'):
#     with ui.tab_panel('A'):
#         ui.label('Content of A')
#     with ui.tab_panel('B'):
#         ui.label('Content of B')
#     with ui.tab_panel('C'):
#         ui.label('Content of C')

# ui.run()
#!/usr/bin/env python3
"""This is just a simple authentication example.

Please see the `OAuth2 example at FastAPI <https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/>`_  or
use the great `Authlib package <https://docs.authlib.org/en/v0.13/client/starlette.html#using-fastapi>`_ to implement a classing real authentication system.
Here we just demonstrate the NiceGUI integration.
"""
from datetime import datetime
from typing import Optional
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from router import Router
from nicegui import app, ui, events, Client
from nicegui.page import page

# in reality users passwords would obviously need to be hashed
passwords = {'user': 'pass'}
router = Router()
unrestricted_page_routes = {'/login'}


class AuthMiddleware(BaseHTTPMiddleware):
    """This middleware restricts access to all NiceGUI pages.

    It redirects the user to the login page if they are not authenticated.
    """

    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('authenticated', False):
            if not request.url.path.startswith('/_nicegui') and request.url.path not in unrestricted_page_routes:
                app.storage.user['referrer_path'] = request.url.path  # remember where the user wanted to go
                return RedirectResponse('/login')
        return await call_next(request)


app.add_middleware(AuthMiddleware)

def on_card_click(e: events.ClickEventArguments, i: int):
    ui.notify(f'Card {i} clicked: {e}')


@ui.page('/', title="Монтиторинг")
@ui.page('/_{_:path}')  # all other pages will be handled by the router but must be registered to also show the SPA index page
def main_page() -> None:
    with ui.header().classes(replace='row items-center').props('height=100') as header:
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
        ui.label('Система мониторинга').style('font-size: 170%; font-weight: 300')
        
        # with ui.tabs() as tabs:
        #     ui.tab('A')
        #     ui.tab('B')
        #     ui.tab('C')

    # with ui.footer(value=False) as footer:
    #     ui.label('Footer')

    with ui.left_drawer().classes('bg-blue-100').props('width=200') as left_drawer:
        # ui.button('Click me!', color=None, on_click=lambda: ui.notify('You clicked me!'))
        with ui.list():
            ui.item("Главная", on_click=lambda: router.open(show_dashboard)).style('font-size: 170%; font-weight: 300').classes('w-screen h-auto')
            ui.item("Настройки", on_click=lambda: router.open(show_settings)).style('font-size: 170%; font-weight: 300').classes('w-screen h-auto')
            ui.item("Журнал", on_click=lambda: router.open(show_journal)).style('font-size: 170%; font-weight: 300').classes('w-screen h-auto')


    @router.add('/_')
    def show_dashboard():
        with ui.row():
            ui.label(text="Без группы").style('font-color: gray; font-size: 120%; font-weight: 400')
            with ui.grid(columns=6).classes('w-full'):
                for i in range(10):
                    with ui.card().on('click', lambda e, i=i: on_card_click(e, i)):
                        with ui.grid(columns=2).classes('w-full'):
                            type_card = ui.label(text="Имя датчика")
                            type_card = ui.label(text="Температура").style('font-color: gray; font-size: 100%; font-weight: 300')
                            type_card = ui.label(text=f"24 ℃").style('font-size: 130%')


    @router.add('/_settings')
    def show_settings():
        ui.label('Content Two').classes('text-2xl')

    @router.add('/_journal')
    def show_journal():
        with ui.row():
            log = ui.log().classes('w-full h-full')
            for i in range(1000):
                log.push(f"{datetime.now().strftime('%X.%f')} Событие {i}")

    router.frame().classes('w-full p-4 bg-gray-100')
    
    # with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
    #     ui.button(on_click=footer.toggle, icon='contact_support').props('fab')

    # with ui.tab_panels(tabs, value='A').classes('w-full'):
    #     with ui.tab_panel('A'):
    #         ui.label('Content of A')
    #     with ui.tab_panel('B'):
    #         ui.label('Content of B')
    #     with ui.tab_panel('C'):
    #         ui.label('Content of C')





@ui.page('/login', title="Монтиторинг")
def login() -> Optional[RedirectResponse]:
    def try_login() -> None:  # local function to avoid passing username and password as arguments
        if passwords.get(username.value) == password.value:
            app.storage.user.update({'username': username.value, 'authenticated': True})
            ui.navigate.to("/_")  # go back to where the user wanted to go
        else:
            ui.notify('Wrong username or password', color='negative')

    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/_')
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)
    return None


ui.run(favicon="📊", storage_secret='THIS_NEEDS_TO_BE_CHANGED')

@app.exception_handler(404)
async def exception_handler_404(request: Request, exception: Exception):
    with Client(page('')) as client:
        ui.label('Sorry, this page does not exist')
    return client.build_response(request, 404)

@app.exception_handler(500)
async def exception_handler_404(request: Request, exception: Exception):
    with Client(page('')) as client:
        ui.label('Sorry, this page does not exist')
    return client.build_response(request, 500)