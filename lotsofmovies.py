from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Genre, Movie

engine = create_engine('sqlite:///moviecatalog.db?check_same_thread=False')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="admin", email="kingslayer4896@gmail.com")
session.add(User1)
session.commit()

# Movies for Action Genre
genre1 = Genre(user_id=1, name="Action")

session.add(genre1)
session.commit()

movie1 = Movie(user_id=1, name="Avengers: Infinity War",
               poster="https://upload.wikimedia.org/wikipedia/en/4/4d/"
               "Avengers_Infinity_War_poster.jpg", director="Russo Brothers",
               description="The Avengers and their allies must be willing to "
               "sacrifice all in an attempt to defeat the powerful Thanos "
               "before his blitz of devastation and ruin puts an end to the "
               "universe.", genre=genre1)

session.add(movie1)
session.commit()

movie2 = Movie(user_id=1, name="The Dark Knight",
               poster="https://upload.wikimedia.org/wikipedia/en/8/8a/"
               "Dark_Knight.jpg", director="Christopher Nolan",
               description="When the menace known as the Joker emerges from "
               "his mysterious past, he wreaks havoc and chaos on the people "
               "of Gotham. The Dark Knight must accept one of the greatest "
               "psychological and physical tests of his ability to fight "
               "injustice.", genre=genre1)

session.add(movie2)
session.commit()

# Movies for Adventure Genre
genre2 = Genre(user_id=1, name="Adventure")

session.add(genre2)
session.commit()

movie1 = Movie(user_id=1, name="The Lord of the Rings",
               poster="https://upload.wikimedia.org/wikipedia/en/9/9d/"
               "The_Lord_of_the_Rings_The_Fellowship_of_the_Ring_%282001%29_"
               "theatrical_poster.jpg", director="Peter Jackson",
               description="A meek Hobbit from the Shire and eight companions "
               "set out on a journey to destroy the powerful One Ring and save"
               " Middle-earth from the Dark Lord Sauron.", genre=genre2)

session.add(movie1)
session.commit()

movie2 = Movie(user_id=1, name="Star Wars",
               poster="https://upload.wikimedia.org/wikipedia/en/thumb/8/87/"
               "StarWarsMoviePoster1977.jpg/220px-StarWarsMoviePoster1977.jpg",
               director="George Lucas", description="Luke Skywalker joins "
               "forces with a Jedi Knight, a cocky pilot, a Wookiee and two "
               "droids to save the galaxy from the Empire's world-destroying "
               "battle-station, while also attempting to rescue Princess Leia "
               "from the evil Darth Vader.", genre=genre2)

session.add(movie2)
session.commit()

# Movies for Comedy Genre
genre3 = Genre(user_id=1, name="Comedy")

session.add(genre3)
session.commit()

movie1 = Movie(user_id=1, name="The Wolf of Wall Street",
               poster="https://upload.wikimedia.org/wikipedia/en/d/d8/"
               "The_Wolf_of_Wall_Street_%282013%29.png", director="Martin "
               "Scorsese", description="Based on the true story of Jordan "
               "Belfort, from his rise to a wealthy stock-broker living the "
               "high life to his fall involving crime, corruption and the "
               "federal government.", genre=genre3)

session.add(movie1)
session.commit()

movie2 = Movie(user_id=1, name="This is the End",
               poster="https://upload.wikimedia.org/wikipedia/en/thumb/3/36/"
               "This-is-the-End-Film-Poster.jpg/220px-This-is-the-End-Film-"
               "Poster.jpg", director="Seth Rogen", description="6 Los Angeles"
               " celebrities are stuck in James Franco's house after a series "
               "of devastating events just destroyed the city. Inside, the "
               "group not only will have to face with the apocalypse, but "
               "with themselves.", genre=genre3)

session.add(movie2)
session.commit()

# Movies for Crime Genre
genre4 = Genre(user_id=1, name="Crime")

session.add(genre4)
session.commit()

movie1 = Movie(user_id=1, name="Scarface",
               poster="https://upload.wikimedia.org/wikipedia/en/thumb/7/71/"
               "Scarface_-_1983_film.jpg/220px-Scarface_-_1983_film.jpg",
               director="Brian De Palma", description="In Miami in 1980, a "
               "determined Cuban immigrant takes over a drug cartel and "
               "succumbs to greed.", genre=genre4)

session.add(movie1)
session.commit()

movie2 = Movie(user_id=1, name="Pulp Fiction",
               poster="https://upload.wikimedia.org/wikipedia/en/3/3b/"
               "Pulp_Fiction_%281994%29_poster.jpg", director="Quentin "
               "Tarantino", description="The lives of two mob hitmen, a boxer,"
               " a gangster's wife, and a pair of diner bandits intertwine in "
               "four tales of violence and redemption.", genre=genre4)

session.add(movie2)
session.commit()

# Movies for Horror Genre
genre5 = Genre(user_id=1, name="Horror")

session.add(genre5)
session.commit()

movie1 = Movie(user_id=1, name="The Conjuring",
               poster="https://upload.wikimedia.org/wikipedia/en/thumb/1/1f/"
               "Conjuring_poster.jpg/220px-Conjuring_poster.jpg",
               director="James Wan", description="Paranormal investigators Ed "
               "and Lorraine Warren work to help a family terrorized by a dark"
               " presence in their farmhouse.", genre=genre5)

session.add(movie1)
session.commit()

movie2 = Movie(user_id=1, name="Insidious",
               poster="https://upload.wikimedia.org/wikipedia/en/thumb/2/2d/"
               "Insidious_poster.jpg/220px-Insidious_poster.jpg",
               director="James Wan", description="A family looks to prevent "
               "evil spirits from trapping their comatose child in a realm "
               "called The Further.", genre=genre5)

session.add(movie2)
session.commit()


print("Movies Added!")
