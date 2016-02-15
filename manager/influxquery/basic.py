import argparse

from influxdb import InfluxDBClient


def main(host='localhost', port=8086):
    user = 'root'
    password = 'root'
    dbname = 'metrics'
    dbuser = 'root'
    dbuser_password = 'root'
    query = 'select * from /^*/ order by time  desc limit 10;'


    client = InfluxDBClient(host, port, user, password, dbname)

    print("Queying data: " + query)
    result = client.query(query)

    print("Result: {0}".format(result))


def parse_args():
    parser = argparse.ArgumentParser(
            description='example code to play with InfluxDB')
    parser.add_argument('--host', type=str, required=False, default='localhost',
                        help='hostname of InfluxDB http API')
    parser.add_argument('--port', type=int, required=False, default=8086,
                        help='port of InfluxDB http API')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(host=args.host, port=args.port)