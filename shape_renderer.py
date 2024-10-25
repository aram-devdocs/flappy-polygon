import pygame
import math

class ShapeRenderer:
    @staticmethod
    def create_polygon_surface(points, color, width=0):
        # Calculate the bounding box of the polygon
        min_x = min([p[0] for p in points])
        max_x = max([p[0] for p in points])
        min_y = min([p[1] for p in points])
        max_y = max([p[1] for p in points])

        # Create a surface with the size of the bounding box
        width_surf = max_x - min_x
        height_surf = max_y - min_y
        surface = pygame.Surface((width_surf, height_surf), pygame.SRCALPHA)

        # Adjust points to the surface coordinate system
        adjusted_points = [(p[0] - min_x, p[1] - min_y) for p in points]

        # Draw the polygon
        pygame.draw.polygon(surface, color, adjusted_points, width)
        return surface

    @staticmethod
    def create_circle_surface(radius, color, width=0):
        diameter = radius * 2
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (radius, radius), radius, width)
        return surface

    @staticmethod
    def create_rectangle_surface(width, height, color):
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(color)
        return surface
    
    @staticmethod
    def create_line_surface(start_pos, end_pos, color, width=1):
        surface = pygame.Surface((max(start_pos[0], end_pos[0]) + width, max(start_pos[1], end_pos[1]) + width), pygame.SRCALPHA)
        pygame.draw.line(surface, color, start_pos, end_pos, width)
        return surface
    
    @staticmethod
    def create_ellipse_surface(rect, color):
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, color, (0, 0, rect.width, rect.height))
        return surface
    
    @staticmethod
    def create_arc_surface(rect, color, start_angle, stop_angle, width=0):
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.arc(surface, color, (0, 0, rect.width, rect.height), math.radians(start_angle), math.radians(stop_angle), width)
        return surface
    