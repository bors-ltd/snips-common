import configparser


class SnipsConfigParser(configparser.ConfigParser):
    encoding = "utf-8"
    filename = "config.ini"

    def to_dict(self):
        return {
            section: {
                name: option for name, option in sorted(self.items(section))
            }
            for section in self.sections()
        }

    def defaults(self):
        return {}

    @classmethod
    def read_configuration_file(cls):
        config = cls()
        print(
            "Loaded configuration files",
            config.read(cls.filename, encoding=cls.encoding)
        )
        return config.to_dict()
