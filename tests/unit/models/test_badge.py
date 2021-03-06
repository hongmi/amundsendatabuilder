# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from databuilder.models.badge import Badge, BadgeMetadata

from databuilder.models.neo4j_csv_serde import NODE_KEY, NODE_LABEL, \
    RELATION_START_KEY, RELATION_START_LABEL, RELATION_END_KEY, \
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE

db = 'hive'
SCHEMA = 'BASE'
TABLE = 'TEST'
CLUSTER = 'DEFAULT'
badge1 = Badge('badge1', 'column')
badge2 = Badge('badge2', 'column')


class TestBadge(unittest.TestCase):
    def setUp(self) -> None:
        super(TestBadge, self).setUp()
        self.badge_metada = BadgeMetadata(db_name='hive',
                                          schema=SCHEMA,
                                          start_label='Column',
                                          start_key='hive://default.base/test/ds',
                                          cluster=CLUSTER,
                                          badges=[badge1, badge2])

    def test_get_badge_key(self) -> None:
        badge_key = self.badge_metada.get_badge_key(badge1.name)
        self.assertEquals(badge_key, badge1.name)

    def test_create_nodes(self) -> None:
        nodes = self.badge_metada.create_nodes()
        self.assertEquals(len(nodes), 2)

        node1 = {
            NODE_KEY: BadgeMetadata.BADGE_KEY_FORMAT.format(badge=badge1.name),
            NODE_LABEL: BadgeMetadata.BADGE_NODE_LABEL,
            BadgeMetadata.BADGE_CATEGORY: badge1.category
        }
        node2 = {
            NODE_KEY: BadgeMetadata.BADGE_KEY_FORMAT.format(badge=badge2.name),
            NODE_LABEL: BadgeMetadata.BADGE_NODE_LABEL,
            BadgeMetadata.BADGE_CATEGORY: badge2.category
        }

        self.assertTrue(node1 in nodes)
        self.assertTrue(node2 in nodes)

    def test_bad_key_entity_match(self) -> None:
        column_label = 'Column'
        table_key = 'hive://default.base/test'

        self.assertRaises(Exception,
                          BadgeMetadata,
                          db_name='hive',
                          schema=SCHEMA,
                          start_label=column_label,
                          start_key=table_key,
                          cluster=CLUSTER,
                          badges=[badge1, badge2])

    def test_bad_entity_label(self) -> None:
        user_label = 'User'
        table_key = 'hive://default.base/test'
        self.assertRaises(Exception,
                          BadgeMetadata,
                          db_name='hive',
                          schema=SCHEMA,
                          start_label=user_label,
                          start_key=table_key,
                          cluster=CLUSTER,
                          badges=[badge1, badge2])

    def test_create_relation(self) -> None:
        relations = self.badge_metada.create_relation()
        self.assertEquals(len(relations), 2)

        relation1 = {
            RELATION_START_LABEL: self.badge_metada.start_label,
            RELATION_END_LABEL: BadgeMetadata.BADGE_NODE_LABEL,
            RELATION_START_KEY: self.badge_metada.start_key,
            RELATION_END_KEY: BadgeMetadata.get_badge_key(badge1.name),
            RELATION_TYPE: BadgeMetadata.BADGE_RELATION_TYPE,
            RELATION_REVERSE_TYPE: BadgeMetadata.INVERSE_BADGE_RELATION_TYPE,
        }
        relation2 = {
            RELATION_START_LABEL: self.badge_metada.start_label,
            RELATION_END_LABEL: BadgeMetadata.BADGE_NODE_LABEL,
            RELATION_START_KEY: self.badge_metada.start_key,
            RELATION_END_KEY: BadgeMetadata.get_badge_key(badge2.name),
            RELATION_TYPE: BadgeMetadata.BADGE_RELATION_TYPE,
            RELATION_REVERSE_TYPE: BadgeMetadata.INVERSE_BADGE_RELATION_TYPE,
        }

        self.assertTrue(relation1 in relations)
        self.assertTrue(relation2 in relations)
