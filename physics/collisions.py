

import collision
import pymunk
import baopig as bp


COLLTYPE_FIGHTER = 0
COLLTYPE_BOUNDARY = 1

# WARNING : with these abort functions, if two shapes are colliding
# with another during the same step, and the first collision affects
# a body's position or velocity, the second collision is almost sure
# to not behave correctly


def abort_collision_poly_solidpoint(poly, solidpoint):
    """If the solidpoint didn't step back the poly, return True"""
    # TODO or WARNING : this function disable boundary frictions, might be a lot of work to implement them

    def dist(point, segment):
        """Return the distance from a point to the line of a segment"""
        AP = point - segment[0]
        AB = segment[1] - segment[0]
        return (AP - AP.projection(AB)).length

    def signed_dist(point, segment):
        """Return the distance from point to segment in normal direction"""
        if pymunk.Vec2d.cross(segment[1] - segment[0], point - segment[0]) > 0:
            return dist(point, segment)
        else:
            return - dist(point, segment)

    try:

        if poly.body.velocity == (0, 0):
            return False
        # This ugly code queries wich shape's edge entered in collision with the solidpoint
        # TODO : rewrite
        COLLISION_TOLERANCE = 4
        velocity = collision.Poly(solidpoint.pos, (collision.Vector(0, 0), poly.body.velocity * COLLISION_TOLERANCE))
        colliding_edge = None
        vertices = poly.rotated_vertices
        for i in range(len(vertices)):
            edge = collision.Poly(poly.body.position, (vertices[i-1], vertices[i]))
            if collision.collide(velocity, edge):
                colliding_edge = edge
                break
        if colliding_edge is None:
            return True

        distance = signed_dist(solidpoint.pos, colliding_edge.points)

        # NOTE : real point formula :
        # point = (vertice + body.position + body.center_of_gravity).rotate(body.angle)

        if bp.debug_with_assert: assert distance > 0
        distance += 1  # don't collide, 1 pixel distance

        edge_normal = pymunk.Vec2d(colliding_edge.points[1] - colliding_edge.points[0]).perpendicular_normal()
        impulse = edge_normal * distance

        if not solidpoint.can_impulse(impulse):
            return True  # boundary's work

        # poly.controller.collide_solidpoint(solidpoint, impulse)
        poly.controller.step_back(*impulse)

        space = poly.body.space
        if space.painter.debug_collisions:
            c = bp.Circle(space.painter, (0, 0, 0), solidpoint.pos, int(max(3, distance * 5)), 1)
            bp.Timer(space.dt, c.kill).start()
            l = bp.Circle(space.painter, (255, 0, 0), solidpoint.pos, 2)
            bp.Timer(space.dt, l.kill).start()

        solidpoint.has_collided = True


        return False
    except Exception as e:
        raise e


# TODO : solve : a fighter without velocity is not bumped out from plateforms


def abort_collision_poly_boundary(arbiter, space, _):

    def dist(point, segment):
        """Return the distance from a point to the line of a segment"""
        AP = point - segment.a
        AB = segment.b - segment.a
        return (AP - AP.projection(AB)).length

    def signed_dist(point, segment):
        """Return the distance from point to segment in normal direction"""
        if (segment.b - segment.a).cross(point - segment.a) > 0:
            return dist(point, segment)
        else:
            return - dist(point, segment)

    try:

        poly = arbiter.shapes[0]
        assert poly.body.COLLTYPE == COLLTYPE_FIGHTER
        boundary = arbiter.shapes[1]
        assert boundary.COLLTYPE == COLLTYPE_BOUNDARY

        for solidpoint in boundary.endpoints:

            if solidpoint.has_collided:
                return False

            if solidpoint.inside(poly):
                if abort_collision_poly_solidpoint(poly, solidpoint) is False:

                    # print(solidpoint.prev_boundary.endpoints[0], solidpoint, solidpoint.next_boundary.endpoints[1])

                    # if boundary is from a plateform:
                    solidpoint.prev_boundary.endpoints[0].has_collided = True
                    solidpoint.next_boundary.endpoints[1].has_collided = True

                    # try: solidpoint.prev_boundary.endpoints[0].has_collided = True
                    # except AttributeError: pass  # 'NoneType' object has no attribute 'endpoints'
                    # try: solidpoint.next_boundary.endpoints[1].has_collided = True
                    # except AttributeError: pass  # 'NoneType' object has no attribute 'endpoints'

                    return False

        # A boundary only block in one way, wich is the normal
        if boundary.normal.dot(poly.body.velocity) >= -.0001: return False

        if space.painter.debug_collisions:
            try:
                for p in arbiter.contact_point_set.points:
                    c = bp.Circle(space.painter, (0, 0, 0), p.point_a, int(max(3, p.distance * 5)), 1)
                    bp.Timer(space.dt, c.kill).start()
                    c = bp.Circle(space.painter, (0, 0, 0), p.point_b, int(max(3, p.distance * 5)), 1)
                    bp.Timer(space.dt, c.kill).start()
            except AttributeError as e:
                # Happen when this function is called from the high velocity solver
                assert str(e) == "'Object' object has no attribute 'contact_point_set'"
                # TODO : make it work
                pass

        if poly.body.velocity != (0, 0) and True:
            # When a poly collides a Boundary, if the first contact was not from a poly's vertex
            # (but from a poly's edge colliding a boundary's extremity), the Boundary shouldn't
            # step back the associated body. This advanced algorithm is a first contact detection

            # When the velocity is too high, the movement_polygon might directly stand behind the boundary.
            # This cause the collision is not detected and the body goes throught the boundary.
            # COLLISION_TOLERANCE is a value that expand the movement_polygon in the direction of where
            # the body comes from, so we are almost sure to find out when the collision needs to occur.
            # This is very usefull when a poly suddenly change size or appear colliding a boundary
            # NOTE : When the body still go through the boundary, it might be because the collision
            # haven't been detected
            COLLISION_TOLERANCE = 200

            # On reconstitue un polygone formé des vertex qui sont passés derrière la Boundary ainsi
            # que ces mêmes vertex avant l'application de la vélocité. Si la barrière est en collision
            # avec ce polygone, alors on recule le player pour qu'il ne touche plus la Boundary
            movement_polygon_points = []
            for v in poly.rotated_vertices:
                if signed_dist(v + poly.body.position, boundary) > 0:
                    movement_polygon_points.insert(0, v)
                    movement_polygon_points.append(v - poly.body.velocity * space.dt * COLLISION_TOLERANCE)
            if not movement_polygon_points: return False  # no vertex behind the boundary
            movement_polygon = collision.Poly(poly.body.position, movement_polygon_points)
            boundary_polygon = collision.Poly((0, 0), (boundary.b, boundary.a))
            if not collision.collide(movement_polygon, boundary_polygon):
                # Here, the first contact is between a poly's edge and a boundary extremity
                if space.painter.debug_boundary_stepback:  # TODO : remove this ?
                    print(movement_polygon)
                    print(boundary_polygon)
                    print("Skipped collision")
                    p = bp.Polygon(space.painter, (255, 128, 128), movement_polygon.points)
                    bp.Timer(space.dt, p.kill).start()
                return False

        distance = 0
        for v in poly.iget_world_vertices():
            if boundary.d.cross(v - boundary.a) > 0:
                distance_v = dist(v, boundary)
                if distance_v > distance:
                    distance = distance_v
        if distance is 0:
            return False
        distance += 1  # don't collide, 1 pixel distance
        impulse = boundary.normal * distance
        if impulse == (0, 0):
            return False

        poly.controller.step_back(*impulse)

        boundary.collidepoly(poly)

        if space.painter.debug_collisions:
            l = bp.Line(space.painter, (255, 0, 0), boundary.a, boundary.b)
            bp.Timer(space.dt*3, l.kill).start()

        return False
    except Exception as e:
        raise e
