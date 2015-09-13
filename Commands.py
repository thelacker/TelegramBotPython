# -*- coding: utf-8 -*-

commands = {} # словарь команд вида   команда: функция
statuses = {'l':'/grouplist', 'g':'/greeting'} # словарь состояний разговора

__no_help_text = "К сожалению для этой команды справки ещё нет"


def define_command(help_text=__no_help_text, cover_wrapped_function=True, special_name=None):

    def decorator(function):
        # в идеале декоратор сам должен писать botFather'у о имеющихся у него командах

        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)

        wrapper.command = special_name if special_name != None else "/{command_name}".format(command_name=function.__name__)
        wrapper.help_text = help_text

        if cover_wrapped_function:
            wrapper.__doc__ = function.__doc__
            wrapper.__name__ = function.__name__

        commands.update({wrapper.command: wrapper})

        return wrapper

    return decorator

