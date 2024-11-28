import argparse

from src.core.domain.book import BookStatus
from src.core.dto.book_dto import BookDTO
from src.core.ports.database import DatabaseInterface
from src.core.usecase import addBookUsecase, deleteBookUsecase, getBookUsecase, setBookStatusUsecase


class CLIAdapter:
    def __init__(
        self,
        database: DatabaseInterface,
        add_book_usecase: addBookUsecase,
        delete_book_usecase: deleteBookUsecase,
        get_book_usecase: getBookUsecase,
        set_book_status_usecase: setBookStatusUsecase,
    ):
        self.add_book_usecase = add_book_usecase
        self.delete_book_usecase = delete_book_usecase
        self.get_book_usecase = get_book_usecase
        self.set_book_status_usecase = set_book_status_usecase
        self.database = database

    @property
    def session(self):
        return self.database.begin_transaction()

    def run(self):
        parser = argparse.ArgumentParser(description="Book Management CLI")
        subparsers = parser.add_subparsers(dest="command")

        add_parser = subparsers.add_parser("add", help="Add a new book")
        add_parser.add_argument("title", type=str, help="Title of the book")
        add_parser.add_argument("author", type=str, help="Author of the book")
        add_parser.add_argument("year", type=int, help="Year of publication")
        add_parser.add_argument(
            "status", choices=[status.value for status in BookStatus], help="Status of the book"
        )

        delete_parser = subparsers.add_parser("delete", help="Delete a book")
        delete_parser.add_argument("id", type=int, help="ID of the book to delete")

        get_parser = subparsers.add_parser("get", help="Get a book")
        get_parser.add_argument("id", type=int, help="ID of the book to get")

        set_parser = subparsers.add_parser("set_status", help="Set the status of a book")
        set_parser.add_argument("id", type=int, help="ID of the book to set the status")
        set_parser.add_argument(
            "status", choices=[status.value for status in BookStatus], help="Status of the book"
        )

        args = parser.parse_args()

        if args.command == "add":
            try:
                book = BookDTO(args.title, args.author, args.year, args.status)
                book_id = self.add_book_usecase.execute(book, self.session)
                print(f"\nBook with id {book_id} added\n")
            except Exception as e:
                print(e)
                add_parser.print_help()
        elif args.command == "delete":
            try:
                self.delete_book_usecase.execute(args.id, self.session)
            except Exception as e:
                print(e)
                delete_parser.print_help()
        elif args.command == "get":
            try:
                book = self.get_book_usecase.execute(args.id, self.session)
                if book:
                    print(book)
                else:
                    print(f"Book with {args.id=} not found")
            except Exception as e:
                print(e)
                get_parser.print_help()
        elif args.command == "set_status":
            try:
                book = self.set_book_status_usecase.execute(args.id, args.status, self.session)
                print(book)
            except Exception as e:
                print(e)
                set_parser.print_help()
        else:
            parser.print_help()
