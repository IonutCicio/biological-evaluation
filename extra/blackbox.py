from __future__ import annotations

# from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import psycopg
    from psycopg.rows import TupleRow


@dataclass(frozen=True)
class Blackbox:
    name: str
    parameters: set[str]

    def register(self, pg_connection: psycopg.Connection[TupleRow]) -> None:
        """Register the blackbox in the database before running the simulations."""
        with pg_connection.transaction():
            pg_cursor = pg_connection.cursor()
            with pg_connection.transaction():
                _ = pg_cursor.execute("SET CONSTRAINTS ALL DEFERRED").execute(
                    "INSERT INTO Blackbox (name) VALUES (%(name)s) ON CONFLICT DO NOTHING",
                    {"name": self.name},
                )

                for parameter in self.parameters:
                    _ = pg_cursor.execute(
                        "INSERT INTO Parameter (key, blackbox) VALUES (%(key)s, %(blackbox)s) ON CONFLICT DO NOTHING",
                        {"key": parameter, "blackbox": self.name},
                    )


# N - nitrogen
# P - phosphorus
# K - potassium

GREEN_BEANS: Blackbox = Blackbox(name="green_beans", parameters={"N", "P", "K"})
