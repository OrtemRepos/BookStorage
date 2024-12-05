from dishka import Provider, Scope, from_context, provide

from src.config import Config
from src.core.ports.database import DatabaseInterface, WriteAheadLogInterface
from src.core.ports.repository import BookRepositoryInterface
from src.core.service.book_service import BookService
from src.core.usecase import addBookUsecase, deleteBookUsecase, getBookUsecase, setBookStatusUsecase
from src.infrastructure.book_repository import BookRepository
from src.infrastructure.cli_adapter import CLIAdapter
from src.infrastructure.database.json_database import JsonDatabase
from src.infrastructure.database.write_ahead_logger import WriteAheadLog


class CLIAdapterProvider(Provider):
    scope = Scope.APP
    config = from_context(provides=Config, scope=Scope.APP)

    @provide
    def provide_wal(self, config: Config) -> WriteAheadLogInterface:
        return WriteAheadLog(config.wal.filepath)

    @provide
    def provide_database(self, wal: WriteAheadLogInterface, config: Config) -> DatabaseInterface:
        return JsonDatabase(config.database.filepath, wal)

    @provide
    def provide_repository(self) -> BookRepositoryInterface:
        return BookRepository()

    @provide
    def provide_service(self, repository: BookRepositoryInterface) -> BookService:
        return BookService(repository=repository)

    @provide
    def provide_add_book_usecase(self, service: BookService) -> addBookUsecase:
        return addBookUsecase(service=service)

    @provide
    def provide_get_book_usecase(self, service: BookService) -> getBookUsecase:
        return getBookUsecase(service=service)

    @provide
    def provide_delete_book_usecase(self, service: BookService) -> deleteBookUsecase:
        return deleteBookUsecase(service=service)

    @provide
    def provide_set_book_status_usecase(self, service: BookService) -> setBookStatusUsecase:
        return setBookStatusUsecase(service=service)

    @provide
    def provide_cli_adapter(
        self,
        database: DatabaseInterface,
        add_book_usecase: addBookUsecase,
        delete_book_usecase: deleteBookUsecase,
        get_book_usecase: getBookUsecase,
        set_book_usecase: setBookStatusUsecase,
    ) -> CLIAdapter:
        return CLIAdapter(
            database, add_book_usecase, delete_book_usecase, get_book_usecase, set_book_usecase
        )
