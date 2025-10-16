import logging

from django.core.management import BaseCommand, CommandError

from apps.websocket import DEFAULT_CHANNEL_LAYER
from apps.websocket.layers import get_channel_layer
from apps.websocket.routing import get_default_application
from apps.websocket.worker import Worker

logger = logging.getLogger("django.channels.worker")


class Command(BaseCommand):
    leave_locale_alone = True
    worker_class = Worker

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--layer",
            action="store",
            dest="layer",
            default=DEFAULT_CHANNEL_LAYER,
            help="Channel layer alias to use, if not the default.",
        )
        # nargs=N（N 为正整数）：命令行参数将被视为一个固定长度的列表，其中包含 N 个参数。用户必须在命令行中输入 N 个参数。
        parser.add_argument("channels", nargs="+", help="Channels to listen on.")

    def handle(self, *args, **options):
        # Get the backend to use
        self.verbosity = options.get("verbosity", 1)
        # Get the channel layer they asked for (or see if one isn't configured)
        # 创建一个指定的通道实例
        if "layer" in options:
            self.channel_layer = get_channel_layer(options["layer"])
        else:
            self.channel_layer = get_channel_layer()
        if self.channel_layer is None:
            # 没有配置 settings.CHANNEL_LAYERS
            raise CommandError("You do not have any CHANNEL_LAYERS configured.")
        # Run the worker
        logger.info("Running worker for channels %s", options["channels"])
        worker = self.worker_class(
            application=get_default_application(),
            channels=options["channels"],
            channel_layer=self.channel_layer,
        )
        worker.run()
