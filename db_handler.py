# generic sqlite database handler
__author__ = 'Salvatore Carotenuto of StartupSolutions'

from sqlalchemy import create_engine, Column, ForeignKey, Integer, Float, String, Boolean, inspect, or_, and_, not_, func
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
import datetime
import hashlib
import json


Base = declarative_base()


# === Helper mixin class ===============================================================================================

# code taken from http://blog.mmast.net/sqlalchemy-serialize-json
class OutputMixin(object):
    RELATIONSHIPS_TO_DICT = False

    def __iter__(self):
        return self.to_dict().iteritems()

    def to_dict(self, rel=None, backref=None):
        if rel is None:
            rel = self.RELATIONSHIPS_TO_DICT
        res = {column.key: getattr(self, attr)
               for attr, column in self.__mapper__.c.items()}
        if rel:
            for attr, relation in self.__mapper__.relationships.items():
                # Avoid recursive loop between to tables.
                if backref == relation.table:
                    continue
                value = getattr(self, attr)
                if value is None:
                    res[relation.key] = None
                elif isinstance(value.__class__, DeclarativeMeta):
                    res[relation.key] = value.to_dict(backref=self.__table__)
                else:
                    res[relation.key] = [i.to_dict(backref=self.__table__)
                                         for i in value]
        return res

    def to_json(self, rel=None):
        def extended_encoder(x):
            if isinstance(x, datetime):
                return x.isoformat()
            #if isinstance(x, UUID):
            #    return str(x)
        if rel is None:
            rel = self.RELATIONSHIPS_TO_DICT
        return json.dumps(self.to_dict(rel), default=extended_encoder)


# === Models ===========================================================================================================


# contains system settings
class Item(OutputMixin, Base):
    __tablename__ = 'items'
    #
    id            = Column(Integer, primary_key=True)
    name          = Column(String)
    description   = Column(String)



# === Handler ==========================================================================================================


class DBHandler():

    def __init__(self, **kwargs):
        if 'database_file' in kwargs:
            self.engine = create_engine('sqlite:///' + kwargs['database_file'])
            Base.metadata.create_all(self.engine)
            print "db created: ", kwargs['database_file']
            Session = sessionmaker(bind=self.engine)
            self.session = Session()



    def get_model_by_tablename(self, tablename):
        """Return class reference mapped to table.

        :param tablename: String with name of table.
        :return: Class reference or None.
        """
        for model in Base._decl_class_registry.values():
            if hasattr(model, '__tablename__') and model.__tablename__ == tablename:
                return model
        return None


    def object_as_dict(self, obj):
        return {c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs}


    def create(self, collection, data):
        resp = { 'success': False }
        try:
            model = self.get_model_by_tablename(collection)
            instance = model(**data)
            self.session.add(instance)
            self.session.commit()
            self.session.refresh(instance)
            resp['success'] = True
            resp['id'] = instance.id
        except Exception as e:
            resp['message'] = str(e)
        #
        return resp


    def create_or_update(self, collection, data, **kwargs):
        resp = { 'success': False }
        try:
            model = self.get_model_by_tablename(collection)
            instance = self.session.query(model).filter_by(**kwargs).first()
            if instance:
                for key, value in data.iteritems():
                    setattr(instance, key, value)
                self.session.commit()
                self.session.refresh(instance)
                resp['success'] = True
                resp['id'] = instance.id
                print "data UPDATED on collection", collection
                #return instance
            else:
                instance = model(**data)
                self.session.add(instance)
                self.session.commit()
                self.session.refresh(instance)
                resp['success'] = True
                resp['id'] = instance.id
                print "data CREATED on collection", collection
        except Exception as e:
            resp['message'] = str(e)
        #
        return resp


    def delete(self, collection, **kwargs):
        resp = { 'success': False }
        try:
            model = self.get_model_by_tablename(collection)
            instance = self.session.query(model).filter_by(**kwargs).first()
            if instance:
                resp['id'] = instance.id
                self.session.delete(instance)
                self.session.commit()
                resp['success'] = True
        except Exception as e:
            resp['message'] = str(e)
        #
        return resp


    def delete_many(self, collection, filters=None, filter_mode='or'):
        resp = { 'success': True }
        #
        model = self.get_model_by_tablename(collection)
        #
        q = self.session.query(model)
        #
        query_filters = []
        if(filters):
            for f in filters:
                if f['op'] == 'eq' or f['op'] == '==':
                    query_filters.append(model.__table__.columns[f['attr']] == f['val'])
                elif f['op'] == 'lt' or f['op'] == '<':
                    query_filters.append(model.__table__.columns[f['attr']] < f['val'])
                elif f['op'] == 'le' or f['op'] == '<=':
                    query_filters.append(model.__table__.columns[f['attr']] <= f['val'])
                elif f['op'] == 'gt' or f['op'] == '>':
                    query_filters.append(model.__table__.columns[f['attr']] > f['val'])
                elif f['op'] == 'ge' or f['op'] == '>=':
                    query_filters.append(model.__table__.columns[f['attr']] >= f['val'])
                elif f['op'] == 'like':
                    query_filters.append(model.__table__.columns[f['attr']].like(f['val']))
            #global rows
            if len(query_filters):
                if filter_mode == 'or':
                    q = q.filter(or_(*query_filters))
                elif filter_mode == 'and':
                    q = q.filter(and_(*query_filters))
        #
        resp['items'] = q.delete()
        self.session.commit()
        print "@@@@ DELETE_MANY RESULT:", resp['items']
        #
        return resp


    def get_collection(self, collection, filters=None, filter_mode='or', order_by=None, include_relationships=True):
        model = self.get_model_by_tablename(collection)
        results = []
        rows = None
        #
        q = self.session.query(model)
        #
        query_filters = []
        if(filters):
            for f in filters:
                if f['op'] == 'eq' or f['op'] == '==':
                    query_filters.append(model.__table__.columns[f['attr']] == f['val'])
                elif f['op'] == 'lt' or f['op'] == '<':
                    query_filters.append(model.__table__.columns[f['attr']] < f['val'])
                elif f['op'] == 'le' or f['op'] == '<=':
                    query_filters.append(model.__table__.columns[f['attr']] <= f['val'])
                elif f['op'] == 'gt' or f['op'] == '>':
                    query_filters.append(model.__table__.columns[f['attr']] > f['val'])
                elif f['op'] == 'ge' or f['op'] == '>=':
                    query_filters.append(model.__table__.columns[f['attr']] >= f['val'])
                elif f['op'] == 'like':
                    query_filters.append(model.__table__.columns[f['attr']].like(f['val']))
            global rows
            if len(query_filters):
                if filter_mode == 'or':
                    q = q.filter(or_(*query_filters))
                elif filter_mode == 'and':
                    q = q.filter(and_(*query_filters))
            #
            if order_by is not None:
                q = q.order_by(order_by['attr'] + ' ' + order_by['direction'])
        #
        rows = q.all()
        #
        #resultset = []
        for item in rows:
            results.append(item.to_dict(rel=include_relationships))
        #
        return results


    def get_first(self, collection, filters=None, filter_mode='or', order_by=None, include_relationships=True):
        results = self.get_collection(collection, filters=filters, filter_mode=filter_mode, order_by=order_by, include_relationships=include_relationships)
        print "---- get_first:"
        print results
        print "---------------"
        if len(results):
            return results[0]
        return None


    def get_max(self, collection, column):
        model = self.get_model_by_tablename(collection)
        max = self.session.query(func.max(model.__table__.columns[column])).scalar()
        print "MAX:", max
        return max

