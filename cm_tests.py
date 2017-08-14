# Copyright 2017 CrowdMaster Developer Team
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of CrowdMaster.
#
# CrowdMaster is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CrowdMaster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CrowdMaster.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

import os
import unittest

import bpy
from bpy.types import Operator
import bmesh

from .cm_syncManager import SyncManagerTestCase


class AddonRegisterTestCase(unittest.TestCase):
    def setUp(self):
        self.play_animation = bpy.context.user_preferences.addons[
            __package__].preferences.play_animation
        bpy.ops.wm.read_homefile()
        bpy.context.user_preferences.addons[__package__].preferences.play_animation = False

    def tearDown(self):
        bpy.context.user_preferences.addons[__package__].preferences.play_animation = self.play_animation

    def testStartStopSim(self):
        pa = bpy.context.user_preferences.addons[__package__].preferences.play_animation
        bpy.ops.scene.cm_start()
        bpy.ops.scene.cm_stop()

    def testRegistered(self):
        sceneProps = ["cm_actions", "cm_events", "cm_groups",
                      "cm_groups_index", "cm_manual",
                      "cm_paths", "cm_view_details", "cm_view_details_index"]
        for sp in sceneProps:
            self.assertIn(sp, dir(bpy.context.scene))

        opsProps = ["cm_actions_populate", "cm_actions_remove", "cm_agent_add",
                    "cm_agent_add_selected", "cm_agent_nodes_generate",
                    "cm_agents_move", "cm_events_move",
                    "cm_events_populate", "cm_events_remove",
                    "cm_groups_reset",
                    "cm_paths_populate", "cm_paths_remove",
                    "cm_place_deferred_geo", "cm_run_long_tests",
                    "cm_run_short_tests", "cm_save_prefs",
                    "cm_start", "cm_stop"]
        for op in opsProps:
            self.assertIn(op, dir(bpy.ops.scene))


class SimpleSimRunTestCase(unittest.TestCase):
    def testSimpleGen(self):
        testfile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "cm_testBase.blend")
    
        with bpy.data.libraries.load(testfile) as (data_from, data_to):
            data_to.scenes = ["Scene"]

        scene = bpy.context.scene

        ng = bpy.data.node_groups.new("simpleGen", "CrowdMasterAGenTreeType")
        
        object_node = ng.nodes.new("ObjectInputNodeType")
        object_node.location = (-1200, 0)
        object_node.inputObject = "Cube"
        
        template_node = ng.nodes.new("TemplateNodeType")
        template_node.location = (-800, 0)
        template_node.brainType = "simpleSim"
        
        rand_node = ng.nodes.new("RandomPositionNodeType")
        rand_node.location = (-400, 0)
        rand_node.noToPlace = 25
        rand_node.radius = 25.00
        
        gen_node = ng.nodes.new("GenerateNodeType")
        gen_node.location = (0, 0)
        
        links = ng.links
        links.new(object_node.outputs[0], template_node.inputs[0])
        links.new(template_node.outputs[0], rand_node.inputs[0])
        links.new(rand_node.outputs[0], gen_node.inputs[0])

        bpy.ops.scene.cm_agent_nodes_generate(nodeName="Generate", nodeTreeName="simpleGen")

    def testSimpleSim(self):
        scene = bpy.context.scene

        ng = bpy.data.node_groups.new("simpleSim", "CrowdMasterTreeType")

        input_node = ng.nodes.new("NewInputNode")
        input_node.location = (-300, 0)
        input_node.InputSource = "CONSTANT"
        input_node.Constant = 0.1

        output_node = ng.nodes.new("OutputNode")
        output_node.location = (0, 0)
        output_node.Output = 'py'
        links = ng.links
        links.new(input_node.outputs[0], output_node.inputs[0])

        bpy.context.scene.cm_sim_start_frame = 1
        bpy.context.scene.cm_sim_end_frame = 50

        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 50

        bpy.context.user_preferences.addons[__package__].preferences.play_animation = True
        bpy.context.user_preferences.addons[__package__].preferences.ask_to_save = False

        bpy.ops.scene.cm_start()


def createShortTestSuite():
    """Gather all the short tests from this module in a test suite"""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(AddonRegisterTestCase))
    test_suite.addTest(unittest.makeSuite(SyncManagerTestCase))
    return test_suite


def createLongTestSuite():
    """Gather all the long tests from this module in a test suite"""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(SimpleSimRunTestCase))
    return test_suite


class CrowdMaster_run_short_tests(Operator):
    """For tests cases that will run quickly.
    ie. that don't involve running simulations"""
    bl_idname = "scene.cm_run_short_tests"
    bl_label = "Run Short Tests"

    def execute(self, context):
        testSuite = createShortTestSuite()
        test = unittest.TextTestRunner()
        result = test.run(testSuite)
        if not result.wasSuccessful():
            return {'CANCELLED'}
        return {'FINISHED'}


class CrowdMaster_run_long_tests(Operator):
    """For tests cases that will take a long time.
    ie. that involve simulation"""
    bl_idname = "scene.cm_run_long_tests"
    bl_label = "Run Long Tests"

    def execute(self, context):
        testSuite = createLongTestSuite()
        test = unittest.TextTestRunner()
        result = test.run(testSuite)
        if not result.wasSuccessful():
            return {'CANCELLED'}
        return {'FINISHED'}


def register():
    bpy.utils.register_class(CrowdMaster_run_short_tests)
    bpy.utils.register_class(CrowdMaster_run_long_tests)


def unregister():
    bpy.utils.unregister_class(CrowdMaster_run_short_tests)
    bpy.utils.unregister_class(CrowdMaster_run_long_tests)
