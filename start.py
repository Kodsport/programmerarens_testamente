import docker
import os


def main():
    client = docker.from_env()
    image = client.images.build(path='app/', tag='pt-website')

    for item in image[1]:
        for key, value in item.items():
            if key == 'stream':
                text = value.strip()
                if text:
                    print(text)

    basedir = os.path.dirname(__file__)
    userdir_path = os.path.join(basedir, 'app', 'user')

    client.containers.run(
        'pt-website:latest', ports={'6969/tcp': ('127.0.0.1', 6969)},
        remove=True, name='pt-website',
        volumes={userdir_path: {'bind': '/app/user', 'mode': 'rw'}})


if __name__ == '__main__':
    main()
