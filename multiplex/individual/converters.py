def GL5528(version, gain):
    """
    Luminance sensor
    http://www.seeedstudio.com/wiki/Grove_-_Luminance_Sensor
    """
    def func(value):
        return value

    return func

def APDS_9002(version, gain):
    """
    Light sensor
    http://www.seeedstudio.com/wiki/Grove_-_Light_Sensor
    """
    def func(value):
        return value

    return func

def get_converter(model, version, gain):
    if model in db:
        return db[model](version, gain)

    else:
        print "no such converter {}".format(model)
        sys.exit(1)


db = {
    "GL5528"   :    GL5528,
    "APDS-9002": APDS_9002,
}


def main():
    print "\n".join(sorted(db.keys()))


if __name__ == "__main__":
    main()
