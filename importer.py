import csv

from models import Book


def import_from_csv(filepath):
    """Import books from a CSV, skipping any already in the system.

    Return count of new books imported.
    """
    existing_books = {(b.title.lower(), b.author.lower()) for b in Book.load_all()}
    new_books = 0

    try:
        with open(filepath, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            reader.fieldnames = [field.lower().strip() for field in reader.fieldnames]
            for row in reader:
                title = row["title"].strip()
                author = row["author"].strip()

                if (title.lower(), author.lower()) not in existing_books:
                    Book(title, author, float(row["rating"].strip())).save()
                    new_books += 1

    except FileNotFoundError:
        print(f" Error! Couldn't find file at: '{filepath}'")
        return 0
    except KeyError as e:
        print(
            f" Error! Missing column '{e}' in CSV file. "
            f"Expected columns: 'title', 'author', 'rating'."
        )
        return 0
    except ValueError as e:
        print(
            f" Error! Invalid rating value: {e}. "
            f"Ensure 'rating' is a number from 1 to 10, inclusive."
        )
        return 0

    return new_books
