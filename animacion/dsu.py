"""Video explicativo de Disjoint Set Union.

Renderizar con: python -m manim -pqh animacion/dsu.py DSUVideo
"""

import json
import os

import numpy as np
from manim import *


PROJECT_TITLE = "Disjoint Set Union (DSU)"
MEMBERS = "Integrantes: Fabiana Ameri · Joaquín Justo"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "..", "logs")


def load_trace(filename):
	path = os.path.join(LOGS_DIR, filename)
	with open(path) as f:
		return json.load(f)["events"]


def resolve_root(parent, x):
	while parent[x] != x:
		x = parent[x]
	return x


def count_members(parent, root):
	return sum(1 for i in range(len(parent)) if resolve_root(parent, i) == root)


def compute_depths(parent):
	memo = {}

	def depth_of(x):
		if x in memo:
			return memo[x]
		if parent[x] == x:
			memo[x] = 0
			return 0
		d = depth_of(parent[x]) + 1
		memo[x] = d
		return d

	return [depth_of(i) for i in range(len(parent))]


def layout_forest(parent, x_spacing=1.3, y_spacing=0.9, y_top=2.0):
	n = len(parent)
	depth = compute_depths(parent)
	max_depth = max(depth)
	positions = {}
	for d in range(max_depth + 1):
		nodes_here = [i for i in range(n) if depth[i] == d]
		if d == 0:
			nodes_here.sort()
		else:
			nodes_here.sort(key=lambda i: (positions[parent[i]][0], i))
		count = len(nodes_here)
		start_x = -(count - 1) * x_spacing / 2
		for idx, node in enumerate(nodes_here):
			positions[node] = np.array([start_x + idx * x_spacing, y_top - d * y_spacing, 0])
	return positions


def fit_group(group, max_height=4.6, top=2.4):
	if group.height > max_height:
		group.scale_to_fit_height(max_height)
	group.shift(UP * (top - group.get_top()[1]))
	return group


def build_edges(nodes_group, parent, color=YELLOW):
	return VGroup(*[
		make_pointer(nodes_group[i], nodes_group[parent[i]], color)
		for i in range(len(parent)) if parent[i] != i
	])


def make_node(label, point, color=BLUE_C):
	circle = Circle(radius=0.34, color=color, stroke_width=3)
	circle.set_fill(BLACK, opacity=1)
	circle.move_to(point)
	text = Text(str(label), font_size=23, color=WHITE).move_to(circle)
	return VGroup(circle, text)


def make_pointer(child, parent, color=TEAL_C):
	return Arrow(
		child.get_center(),
		parent.get_center(),
		buff=0.38,
		color=color,
		stroke_width=3,
		max_tip_length_to_length_ratio=0.18,
	)


def make_caption(lines):
	caption = VGroup(*[
		Text(line, font_size=21, color=WHITE)
		for line in lines
	]).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
	max_width = config.frame_width - 0.8
	if caption.width > max_width:
		caption.scale_to_fit_width(max_width)
	caption.to_edge(DOWN, buff=0.24)
	return caption


def make_heading(text):
	return Text(text, font_size=32, color=TEAL_C).to_edge(UP, buff=0.3)


class DSUVideo(Scene):
	def construct(self):
		self.opening()
		self.concept()
		self.make_set_demo()
		self.single_element_case()
		self.naive_find_demo()
		self.path_compression_demo()
		self.union_by_size_demo()
		self.complexity_summary()
		self.credits()

	def opening(self):
		title = Text(PROJECT_TITLE, font_size=46, color=TEAL_C)
		subtitle = Text("Una estructura para mantener conjuntos disjuntos", font_size=25)
		members = Text(MEMBERS, font_size=22, color=GRAY_A)
		group = VGroup(title, subtitle, members).arrange(DOWN, buff=0.38)
		self.play(Write(title), run_time=1)
		self.play(FadeIn(subtitle, shift=UP * 0.15), FadeIn(members))
		self.wait(1)
		self.play(FadeOut(group))

	def concept(self):
		heading = make_heading("¿Qué es un DSU?")
		caption = make_caption([
			"Es un TDA que mantiene una partición de elementos en conjuntos disjuntos.",
			"Permite consultar si dos elementos pertenecen al mismo conjunto y unir conjuntos.",
			"Se usa, por ejemplo, para componentes conexas y el algoritmo de Kruskal.",
		])
		self.play(FadeIn(heading, shift=DOWN * 0.15), Write(caption), run_time=1)

		example_positions = {
			0: np.array([-2.5, 0.9, 0]),
			1: np.array([-3.5, -0.4, 0]),
			2: np.array([-1.5, -0.4, 0]),
			3: np.array([2.0, 0.6, 0]),
			4: np.array([3.2, -0.5, 0]),
		}
		group_a_color = BLUE_C
		group_b_color = ORANGE
		example_nodes = {
			i: make_node(i, p, group_a_color if i in (0, 1, 2) else group_b_color)
			for i, p in example_positions.items()
		}
		self.play(LaggedStart(
			*[GrowFromCenter(node) for node in example_nodes.values()],
			lag_ratio=0.15,
		))
		self.wait(0.5)
		edge_1 = make_pointer(example_nodes[1], example_nodes[0], group_a_color)
		edge_2 = make_pointer(example_nodes[2], example_nodes[0], group_a_color)
		edge_3 = make_pointer(example_nodes[4], example_nodes[3], group_b_color)
		self.play(GrowArrow(edge_1), GrowArrow(edge_2), GrowArrow(edge_3))
		self.wait(32)
		self.play(FadeOut(VGroup(
			heading, caption, *example_nodes.values(), edge_1, edge_2, edge_3
		)))

	def make_set_demo(self):
		heading = make_heading("MakeSet: crear conjuntos")
		events = load_trace("dsu_log_main.json")
		init_event = events[0]
		n = init_event["n"]
		positions = layout_forest(init_event["parent_after"], y_top=0.5)
		nodes = VGroup(*[make_node(i, positions[i]) for i in range(n)])
		caption = make_caption([
			"Cada elemento empieza como raíz de su propio conjunto: Parent[x] = x.",
			f"Crear un elemento cuesta O(1); inicializar {n} elementos con makeSet({n}) cuesta O(n).",
		])
		self.play(FadeIn(heading), LaggedStart(*[GrowFromCenter(node) for node in nodes], lag_ratio=0.15))
		self.play(Write(caption), run_time=1)
		self.wait(10.5)
		self.play(FadeOut(VGroup(heading, nodes, caption)))

	def single_element_case(self):
		heading = make_heading("Caso borde: un solo elemento")
		events = load_trace("dsu_log_single.json")
		find_event = next(e for e in events if e["op"] == "find")
		x = find_event["x"]
		root = find_event["root"]
		node = make_node(x, np.array([0, 0.4, 0]))
		tracer = Circle(radius=0.44, color=YELLOW, stroke_width=4)
		tracer.move_to(node.get_center())
		caption = make_caption([
			f"makeSet(1) crea un único elemento: Parent[{x}] = {x}.",
			f"Find({x}) retorna de inmediato porque es su propia raíz ({root}): caso base de la recursión.",
		])
		self.play(FadeIn(heading), GrowFromCenter(node))
		self.play(FadeIn(tracer), Write(caption), run_time=1)
		self.wait(12)
		self.play(FadeOut(VGroup(heading, node, tracer, caption)))

	def naive_find_demo(self):
		heading = make_heading("Find sin optimizaciones")
		events = load_trace("dsu_log_worstcase.json")
		find_event = next(e for e in events if e["op"] == "find")
		parent = find_event["parent_before"]
		path = find_event["path"]
		x = find_event["x"]
		root = find_event["root"]
		n = len(parent)
		positions = layout_forest(parent)
		nodes = VGroup(*[make_node(i, positions[i], BLUE_C) for i in range(n)])
		edges = build_edges(nodes, parent, YELLOW)
		fit_group(VGroup(nodes, edges))
		caption = make_caption([
			"Una secuencia de uniones sin optimizar puede formar una cadena.",
			f"Find({x}) recorre hasta la raíz {root}: O(n) en el peor caso.",
		])
		tracer = Circle(radius=0.44, color=YELLOW, stroke_width=4)
		tracer.move_to(nodes[path[0]].get_center())

		self.play(FadeIn(heading), LaggedStart(*[FadeIn(node) for node in nodes], lag_ratio=0.1))
		self.play(LaggedStart(*[GrowArrow(edge) for edge in edges], lag_ratio=0.12))
		self.play(Write(caption), FadeIn(tracer), run_time=1)
		for step in path[1:]:
			self.play(tracer.animate.move_to(nodes[step].get_center()), run_time=0.45)
		self.wait(5)
		self.play(FadeOut(VGroup(heading, nodes, edges, caption, tracer)))

	def path_compression_demo(self):
		heading = make_heading("Find con path compression")
		events = load_trace("dsu_log_worstcase.json")
		find_event = next(e for e in events if e["op"] == "find")
		parent_before = find_event["parent_before"]
		parent_after = find_event["parent_after"]
		x = find_event["x"]
		root = find_event["root"]
		n = len(parent_before)

		chain_positions = layout_forest(parent_before)
		chain_nodes = VGroup(*[
			make_node(i, chain_positions[i], YELLOW if i == x else BLUE_C)
			for i in range(n)
		])
		chain_edges = build_edges(chain_nodes, parent_before, YELLOW)
		fit_group(VGroup(chain_nodes, chain_edges))

		flat_positions = layout_forest(parent_after)
		flat_nodes = VGroup(*[
			make_node(i, flat_positions[i], YELLOW if i == x else BLUE_C)
			for i in range(n)
		])
		flat_edges = build_edges(flat_nodes, parent_after, YELLOW)
		fit_group(VGroup(flat_nodes, flat_edges))

		caption = make_caption([
			f"Find({x}) encuentra la raíz {root} y cambia los padres de los nodos visitados.",
			"La cadena se aplana; con compresión sola, Find es O(log n) amortizado.",
		])
		self.play(FadeIn(heading), FadeIn(chain_nodes), Create(chain_edges))
		self.play(Write(caption), run_time=1)
		self.wait(1)
		self.play(Transform(chain_nodes, flat_nodes), Transform(chain_edges, flat_edges), run_time=2)
		self.wait(9)
		self.play(FadeOut(VGroup(heading, chain_nodes, chain_edges, caption)))

	def union_by_size_demo(self):
		heading = make_heading("Unión por tamaño")
		events = load_trace("dsu_log_main.json")
		event = [e for e in events if e["op"] == "union"][-1]
		parent_before = event["parent_before"]
		n = len(parent_before)
		ra = event["new_root"]
		rb = event["attached"]
		size_ra = count_members(parent_before, ra)
		size_rb = count_members(parent_before, rb)

		positions = layout_forest(parent_before)
		nodes = VGroup(*[
			make_node(i, positions[i], YELLOW if i in (ra, rb) else BLUE_C)
			for i in range(n)
		])
		edges = build_edges(nodes, parent_before)
		labels = VGroup(
			Text(f"tamaño {size_ra}", font_size=20, color=YELLOW).next_to(nodes[ra], UP, buff=0.18),
			Text(f"tamaño {size_rb}", font_size=20, color=YELLOW).next_to(nodes[rb], UP, buff=0.18),
		)
		caption = make_caption([
			f"Al unir las raíces {ra} y {rb}, el árbol menor "
			f"(tamaño {min(size_ra, size_rb)}) queda bajo el mayor (tamaño {max(size_ra, size_rb)}).",
			"La altura se mantiene en O(log n). Este código usa tamaño, no rango.",
		])
		self.play(FadeIn(heading), FadeIn(nodes), Create(edges), FadeIn(labels))
		self.play(Write(caption), run_time=1)
		self.wait(2)
		new_edge = make_pointer(nodes[rb], nodes[ra], YELLOW)
		self.play(GrowArrow(new_edge), run_time=1.5)
		self.wait(7.5)
		self.play(FadeOut(VGroup(heading, nodes, edges, labels, caption, new_edge)))

	def complexity_summary(self):
		heading = make_heading("Complejidad temporal")
		rows = [
			["MakeSet(x)", "O(1)"],
			["Find(x) sin optimizaciones", "O(n) en el peor caso"],
			["Find(x) con path compression", "O(log n) amortizado"],
			["Union(x, y) con unión por rango", "altura ≤ log₂(n)"],
			["Find(x) / Union(x, y) combinadas", "O(α(n)) amortizado"],
		]
		table = Table(
			rows,
			col_labels=[
				Text("Operación", font_size=24, color=TEAL_C),
				Text("Complejidad", font_size=24, color=TEAL_C),
			],
			include_outer_lines=True,
			line_config={"stroke_color": WHITE, "stroke_width": 2.5},
			element_to_mobject=Text,
			element_to_mobject_config={"font_size": 22, "color": WHITE},
		)
		if table.width > config.frame_width - 1:
			table.scale_to_fit_width(config.frame_width - 1)
		table.next_to(heading, DOWN, buff=0.5)
		self.play(FadeIn(heading))
		self.play(LaggedStart(*[FadeIn(row) for row in table.get_rows()], lag_ratio=0.3))
		self.wait(36.5)
		self.play(FadeOut(VGroup(heading, table)))

	def credits(self):
		title = Text(PROJECT_TITLE, font_size=40, color=TEAL_C)
		members = Text(MEMBERS, font_size=24)
		credits = VGroup(title, members).arrange(DOWN, buff=0.4)
		self.play(FadeIn(credits, shift=UP * 0.2))
		self.wait(4)