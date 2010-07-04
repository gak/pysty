#!/usr/bin/env python
# ConfigOpt: An OptParse/ConfigParser object.

import os.path
import ConfigParser

from optparse import OptionParser, OptionGroup, Option

_true_values = ('True', 'true', 'Yes', 'yes')
_false_values = ('False', 'false', 'No', 'no')

class ReferenceOption(Option):
    def __init__(self, *args, **kwargs):
        if 'group' in kwargs:
            self.group = kwargs['group']
            del kwargs['group']
        else:
            self.group = None

        if 'option' in kwargs:
            self.option = kwargs['option']
            del kwargs['option']
        else:
            self.option = None

        if 'conflict_group' in kwargs:
            self.conflict_group = kwargs['conflict_group']
            del kwargs['conflict_group']
        else:
            self.conflict_group = None

        Option.__init__(self, *args, **kwargs)


class ConfigOptOption(object):
    """An option."""
    def __init__(self, *args, **kwargs):
        if not 'name' in kwargs:
            raise AttributeError, 'Missing option name'

        self.name = kwargs['name']
        del kwargs['name']

        if 'is_cmd_option' in kwargs:
            self._cmd_option = kwargs['is_cmd_option']
            del kwargs['is_cmd_option']
        else:
            self._cmd_option = True # default value

        if 'is_config_option' in kwargs:
            self._config_option = kwargs['is_config_option']
            del kwargs['is_config_option']
        else:
            self._config_option = True

        if 'default' in kwargs:
            self._default = kwargs['default']
            del kwargs['default']   # Remove it so we don't pass it to
                                    # OptionParser -- we have our own defaults
                                    # and, passing it to OptionParser would
                                    # make it always return as set in the
                                    # command line, breaking the behaviour we
                                    # want.
        else:
            self._default = None

        self._params = kwargs
        self._args = args
        self.config_value = None
        self.cmd_value = None
        self._set_value = None

    def _get_value(self):
        """Return the value of a variable."""
        # this is the priority order: First, the value set by the application;
        # if it's not set, use the command line value; if there is no option
        # in the command line, use the config value; if this is also not set,
        # return the default value for the variable.
        if self._set_value is not None:
            return self._set_value

        if self.cmd_value is not None:
            return self.cmd_value

        if self.config_value is not None:
            return self.config_value

        return self._default
    
    def _set_value(self, x):
        """Set the value of the variable. Used by the application to set a
        value for it."""
        self._set_value = x

    value = property(_get_value, _set_value)

    @property
    def args(self):
        return self._args

    @property
    def params(self):
        return self._params

    @property
    def cmd_option(self):
        return self._cmd_option

    @property
    def config_option(self):
        return self._config_option


class ConfigOptGroup(object):
    """A group of options."""
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self.options = {}
        return

    def add_option(self, *args, **kwargs):
        """Add an option in the group."""
        id = kwargs['name']
        if id in self.options:
            return
        self.options[id]= ConfigOptOption(*args, **kwargs)
        return

    def cmd_parser(self, parser):
        """Build the command line parser for the option."""
        group = OptionGroup(parser, self.desc)
        options = 0     # to avoid adding an empty group

        for option_id in self.options:
            option = self.options[option_id]
            if option.cmd_option:
                internal_name = self.name + '_' + option.name   # to avoid
                                                                # clashes
                option_params = option.params
                option_params['dest'] = internal_name
                option_params['group'] = self.name
                option_params['option'] = option.name

                if not 'metavar' in option_params:
                    option_params['metavar'] = option.name.upper()

                group.add_option(*option.args, **option_params)

                options += 1

        if options > 0:
            parser.add_option_group(group)

        return

    def __getitem__(self, key):
        return self.options[key].value

    def __setitem__(self, key, value):
        self.options[key].value = value

class ConfigOpt(object):
    """Command line and config file option merger."""

    def __init__(self, app_name=None):
        """Class initialization. <app_name> is used to create the config file
        in the user home directory."""

        if app_name is None:
            import sys
            filename = os.path.basename(sys.argv[0])
            (name, _) = os.path.splitext(filename)
            app_name = name


        self._config_name = os.path.expanduser(os.path.join('~', '.' +
            app_name + '.ini'))
        self._cmd_parser = OptionParser(option_class=ReferenceOption)

        self._cmd_parser.add_option('-c', '--config',
                dest='config_file',
                help='Configuration file.',
                default = self._config_name)

        self._groups = {}
        self._conflicts = None

    @property
    def conflicts(self):
        """Return the dictionary with the groups in the conflict groups."""
        return self._conflicts

    def add_group(self, id, desc=None):
        """Create a new group of options."""
        if id in self._groups:
            return
        self._groups[id] = ConfigOptGroup(id, desc)
        return

    def add_option(self, *args, **kwargs):
        """Add an option in the list of options."""
        assert 'group' in kwargs
        assert 'option' in kwargs

        group_id = kwargs['group']
        del kwargs['group']

        option_id = kwargs['option']
        del kwargs['option']

        group = self._groups[group_id]
        group.add_option(name=option_id, *args, **kwargs)

    def load(self):
        """Load the options for the config file."""
        config = ConfigParser.SafeConfigParser()
        config.read(self._config_name)

        for section in config.sections():
            if section not in self._groups:
                continue        # ignore this group

            for option in config.options(section):
                if option not in self._groups[section].options:
                    continue

                value = config.get(section, option)
                # Convert boolean values
                if value in _true_values or value in _false_values:
                    value = (value in _true_values)
                self._groups[section].options[option].config_value = value
        return

    def save(self):
        """Save the config file."""
        config = ConfigParser.SafeConfigParser()
        for group in self._groups:
            group_added = False

            for option_id in self._groups[group].options:
                option = self._groups[group].options[option_id]

                if not option.config_option:
                    continue

                if not group_added:
                    # prevents empty groups
                    config.add_section(group)
                    group_added = True

                config.set(group, option.name, str(option.value))

        config_file = file(self._config_name, 'w')
        config.write(config_file)
        config_file.close()
        return

    def __call__(self):
        """Callable object, do the parsing of the command line and loads the
        config file required."""
        for group in self._groups:
            self._groups[group].cmd_parser(self._cmd_parser)

        (options, args) = self._cmd_parser.parse_args()
        self._config_name = options.config_file
        self._conflicts = {}

        for group in self._cmd_parser.option_groups:
            for option in group.option_list:
                group_id = option.group
                option_id = option.option
                value = getattr(options, option.dest)
                conflict_group = option.conflict_group

                if value is None:
                    continue

                if conflict_group and conflict_group in self._conflicts:
                    if group_id != self._conflicts[conflict_group]:
                        self._cmd_parser.error(
                                "You can't mix options from %s and %s." % (
                                    self._conflicts[conflict_group], group_id))
                        return

                self._conflicts[conflict_group] = group_id
                self._groups[group_id].options[option_id].cmd_value = value

        self.load()

    def __getitem__(self, key):
        return self._groups[key]
