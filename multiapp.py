"""Frameworks for running multiple Streamlit applications as a single app.
   Courtesy of dataprofessor (git).
"""
import streamlit as st

class MultiApp:
    """Framework for combining multiple streamlit applications.
    Usage:
        def foo():
            st.title("Hello Foo")
        def bar():
            st.title("Hello Bar")
        app = MultiApp()
        app.add_app("Foo", foo)
        app.add_app("Bar", bar)
        app.run()
    It is also possible keep each application in a separate file.
        import foo
        import bar
        app = MultiApp()
        app.add_app("Foo", foo.app)
        app.add_app("Bar", bar.app)
        app.run()
    """
    def __init__(self):
        self.apps = []

    def add_app(self, title, func, **func_args):
        """Adds a new application.
        Parameters
        ----------
        func:
            the python function to render this app.
        title:
            title of the app. Appears in the dropdown in the sidebar.
        func_args:
            additional arguments, such as a common database.
        """
   
        self.apps.append({
            "title": title,
            "function": func,
            "func_args": {k:arg for k,arg in func_args.items()}
        })


    def run(self):
        # app = st.sidebar.radio(
        app = st.radio(
            'Page',
            self.apps,
            format_func=lambda app: app['title'])
        
        if any(app['func_args']):
            app['function'](**app['func_args'])
        else:
            app['function']()