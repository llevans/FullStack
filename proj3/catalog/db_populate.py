#
# file: db_populate.py
# author: lyn.evans
# date: 09.07.15
#
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Era, Composer
from sqlalchemy.orm import relationship
#
# Populate tables with initial data
#
engine = create_engine('postgresql://vagrant:vagrant@localhost:5432/vagrant')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

m_era1 = Era(name="Early")
session.add(m_era1)
m_era2 = Era(name="Baroque")
session.add(m_era2)
m_era3 = Era(name="Classical")
session.add(m_era3)
m_era4 = Era(name="Romantic")
session.add(m_era4)
m_era5 = Era(name="Renaissance")
session.add(m_era5)
m_era6 = Era(name="Modern")
session.add(m_era6)
m_era7 = Era(name="Contemporary")
session.add(m_era7)
session.commit()

m_descr = "A German composer and musician of the Baroque period. He enriched "
m_descr += "established German styles through his skill in counterpoint, "
m_descr += "harmonic and motivic organization."
m_name = "Johann Sebastian Bach"
m_composer1 = Composer(name=m_name, description=m_descr, era=m_era2)
session.add(m_composer1)
m_descr = "Important composer during the transition from Baroque "
m_descr += "to Classical."
m_name = "Domenico Scarlatti"
m_composer2 = Composer(name=m_name, description=m_descr, era=m_era2)
session.add(m_composer2)
m_descr = "A prominent and prolific Austrian composer of the Classical "
m_descr == "period. He was instrumental in the development of chamber "
m_descr += "music such as the piano trio[1] and his contributions to musical "
m_descr += "form have earned him the epithets 'Father of the Symphony' and "
m_descr += "'Father of the String Quartet.'"
m_composer3 = Composer(name="Joseph Hayden", description=m_descr, era=m_era3)
session.add(m_composer3)
m_name = "Wolfgang Amadeus Mozart"
m_descr = "Prolific and influential"
m_composer4 = Composer(name=m_name, description=m_descr, era=m_era3)
session.add(m_composer4)
m_name = "Ludwig van Beethoven"
m_descr = "Born in Bonn, Germany and established his career in Vienna."
m_composer5 = Composer(name=m_name, description=m_descr, era=m_era4)
session.add(m_composer5)
m_name = "Frederic Francois Chopin"
m_descr = "A Polish composer and virtuoso pianist of the Romantic "
m_descr += "era, who wrote primarily for the solo piano. He gained "
m_descr += "and has maintained renown worldwide as one of the leading "
m_descr += "musicians of his era, whose poetic genius was based on a "
m_descr += "professional technique that was without equal in his generation. "
m_descr += "His etudes are recognized by everyone."
m_composer6 = Composer(name=m_name, description=m_descr, era=m_era4)
session.add(m_composer6)
m_name = "George Phillip Telemann"
m_descr = "Mulit-instramentalist."
m_composer7 = Composer(name=m_name, description=m_descr, era=m_era1)
session.add(m_composer7)
m_descr = "Russian composer who has inaugural concert at Carnegie Hall."
m_name = "Pyotr Ilyich Tchaikovsky"
m_composer8 = Composer(name=m_name, description=m_descr, era=m_era6)
session.add(m_composer8)
m_descr = "Composer of music with repetitive structure 'minimilistic'."
m_name = "Phillip Morris Glass"
m_composer9 = Composer(name=m_name, description=m_descr, era=m_era7)
session.add(m_composer9)
m_descr = "Known for romanticism in russian classical music."
m_name = "Sergei Vassilievich Rachmaninoff"
m_composer10 = Composer(name=m_name, description=m_descr, era=m_era6)
session.add(m_composer10)
m_descr = "Prolific and profound young Chinese composer. He highlights "
m_descr += "Chinese folk music and history into his concertis."
m_composer11 = Composer(name="Peng Peng Gong", description=m_descr, era=m_era7)
session.add(m_composer11)
m_descr = "Technical young American composer introducing powerful "
m_descr += "improvisation to young audiences. Considered 'ultra-modern'. "
m_descr += "Total garage band creator as well."
m_composer12 = Composer(name="Conrad Tao", description=m_descr, era=m_era7)
session.add(m_composer12)
session.commit()
