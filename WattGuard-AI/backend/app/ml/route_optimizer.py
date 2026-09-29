"""WattGuard AI - Vehicle Route Optimization Engine (TSP Solver)
Feature 20:
- Solves Travelling Salesperson Problem (TSP) heuristic: Nearest Neighbor + 2-opt local search.
- Accepts inspector starting GPS coordinates and list of assigned consumer/alert waypoints.
- Outputs ordered sequence, leg distances, travel time estimates, and cumulative inspection tour duration.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from app.ml.geospatial_cluster import GeospatialClusterEngine


class RouteOptimizer:
    """Heuristic TSP vehicle route solver for utility inspection dispatches."""

    def __init__(self, avg_speed_kmh: float = 30.0, inspection_minutes_per_stop: float = 25.0):
        self.avg_speed_kmh = avg_speed_kmh
        self.inspection_minutes_per_stop = inspection_minutes_per_stop
        self.haversine = GeospatialClusterEngine.haversine_distance_km

    def build_distance_matrix(self, points: List[Tuple[float, float]]) -> np.ndarray:
        """Constructs pairwise distance matrix in kilometers."""
        n = len(points)
        dist_matrix = np.zeros((n, n), dtype=float)
        for i in range(n):
            for j in range(i + 1, n):
                d = self.haversine(points[i][0], points[i][1], points[j][0], points[j][1])
                dist_matrix[i, j] = d
                dist_matrix[j, i] = d
        return dist_matrix

    def nearest_neighbor_tour(self, dist_matrix: np.ndarray, start_idx: int = 0) -> List[int]:
        """Greedy nearest neighbor path starting from inspector base."""
        n = len(dist_matrix)
        unvisited = set(range(n))
        unvisited.remove(start_idx)
        tour = [start_idx]

        curr = start_idx
        while unvisited:
            next_stop = min(unvisited, key=lambda idx: dist_matrix[curr, idx])
            tour.append(next_stop)
            unvisited.remove(next_stop)
            curr = next_stop

        return tour

    def two_opt_optimize(self, tour: List[int], dist_matrix: np.ndarray, max_iterations: int = 50) -> List[int]:
        """2-opt heuristic improvement removing cross-paths."""
        best_tour = list(tour)
        improved = True
        iterations = 0

        def tour_distance(t):
            return sum(dist_matrix[t[i], t[i + 1]] for i in range(len(t) - 1))

        best_dist = tour_distance(best_tour)

        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            for i in range(1, len(best_tour) - 1):
                for j in range(i + 1, len(best_tour)):
                    # Reverse slice from i to j
                    new_tour = best_tour[:i] + best_tour[i : j + 1][::-1] + best_tour[j + 1 :]
                    new_dist = tour_distance(new_tour)
                    if new_dist < best_dist - 1e-4:
                        best_tour = new_tour
                        best_dist = new_dist
                        improved = True
                        break
                if improved:
                    break

        return best_tour

    def optimize_route(
        self,
        inspector_start: Tuple[float, float],
        stops: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculates optimal sequence of stops starting from inspector start coordinates.
        
        Args:
            inspector_start: (latitude, longitude) of field inspector.
            stops: List of dicts with:
                alert_id, consumer_id, latitude, longitude, recommended_action, address_or_tag
        Returns:
            Structured route plan with ordered waypoints, leg distances, and timestamps.
        """
        if not stops:
            return {
                "total_stops": 0,
                "total_distance_km": 0.0,
                "estimated_transit_minutes": 0.0,
                "estimated_inspection_minutes": 0.0,
                "estimated_total_tour_minutes": 0.0,
                "ordered_waypoints": []
            }

        all_points = [inspector_start] + [(s["latitude"], s["longitude"]) for s in stops]
        dist_matrix = self.build_distance_matrix(all_points)

        # 1. Greedy Tour from start index 0
        nn_tour = self.nearest_neighbor_tour(dist_matrix, start_idx=0)

        # 2. 2-opt Local Search refinement
        best_tour = self.two_opt_optimize(nn_tour, dist_matrix)

        # Build output waypoints
        ordered_waypoints = []
        cumulative_dist = 0.0
        cumulative_time_mins = 0.0

        for seq, node_idx in enumerate(best_tour):
            if node_idx == 0:
                # Inspector starting location
                wp = {
                    "sequence": seq,
                    "alert_id": None,
                    "consumer_id": None,
                    "latitude": round(inspector_start[0], 6),
                    "longitude": round(inspector_start[1], 6),
                    "address_or_tag": "Inspector Deployment Base / Current GPS",
                    "recommended_action": "ORIGIN_DEPARTURE",
                    "distance_from_prev_km": 0.0,
                    "cumulative_distance_km": 0.0,
                    "estimated_arrival_minutes": 0.0
                }
            else:
                stop_data = stops[node_idx - 1]
                prev_node = best_tour[seq - 1]
                leg_dist = dist_matrix[prev_node, node_idx]
                transit_time = (leg_dist / self.avg_speed_kmh) * 60.0  # in minutes
                cumulative_dist += leg_dist
                cumulative_time_mins += transit_time

                wp = {
                    "sequence": seq,
                    "alert_id": stop_data.get("alert_id"),
                    "consumer_id": stop_data.get("consumer_id"),
                    "latitude": round(stop_data["latitude"], 6),
                    "longitude": round(stop_data["longitude"], 6),
                    "address_or_tag": stop_data.get("address_or_tag", f"Meter {stop_data.get('consumer_id')}"),
                    "recommended_action": stop_data.get("recommended_action", "METER_CALIBRATION_TEST"),
                    "distance_from_prev_km": round(float(leg_dist), 2),
                    "cumulative_distance_km": round(float(cumulative_dist), 2),
                    "estimated_arrival_minutes": round(float(cumulative_time_mins), 1)
                }
                # Add inspection duration to elapsed time for subsequent legs
                cumulative_time_mins += self.inspection_minutes_per_stop

            ordered_waypoints.append(wp)

        total_transit_mins = (cumulative_dist / self.avg_speed_kmh) * 60.0
        total_inspection_mins = len(stops) * self.inspection_minutes_per_stop
        total_tour_mins = total_transit_mins + total_inspection_mins

        return {
            "total_stops": len(stops),
            "total_distance_km": round(float(cumulative_dist), 2),
            "estimated_transit_minutes": round(float(total_transit_mins), 1),
            "estimated_inspection_minutes": round(float(total_inspection_mins), 1),
            "estimated_total_tour_minutes": round(float(total_tour_mins), 1),
            "ordered_waypoints": ordered_waypoints
        }


route_optimizer_instance = RouteOptimizer()
