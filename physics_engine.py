"""
Physics calculation engine for ForceQuest
Handles all force, work, energy, and power calculations
"""
import math
from config import GRAVITY, SURFACE_FRICTION, SHAPE_FRICTION_FACTOR, FORCE_ANGLE_MAP


class PhysicsCalculator:
    """Handles all physics computations for the simulation"""
    
    def __init__(self):
        self.g = GRAVITY
    
    def get_effective_friction(self, surface, shape, user_mu=None):
        """Calculate effective friction coefficient"""
        if user_mu is not None:
            return user_mu
        
        base_mu = SURFACE_FRICTION.get(surface, 0.5)
        friction_factor = SHAPE_FRICTION_FACTOR.get(shape, 1.0)
        return base_mu * friction_factor
    
    def calculate_normal_force(self, mass, scenario, angle, force, force_angle):
        """Calculate normal force based on scenario"""
        weight = mass * self.g
        F_vertical = (force if force else 0) * math.sin(math.radians(force_angle))
        
        if scenario == "Inclined Plane":
            Fn = weight * math.cos(math.radians(angle))
        else:
            Fn = weight - F_vertical
        
        return max(Fn, 0)
    
    def calculate_required_force(self, mass, scenario, angle, mu, Fn):
        """Calculate minimum force required to move the object"""
        weight = mass * self.g
        
        if scenario == "Lifting Object":
            return weight
        elif scenario == "Inclined Plane":
            return weight * math.sin(math.radians(angle)) + mu * Fn
        else:  # Pushing Object
            return mu * Fn
    
    def calculate_mass_from_force(self, force, scenario, angle, mu):
        """Calculate mass when not provided"""
        if scenario == "Lifting Object":
            return force / self.g
        elif scenario == "Inclined Plane":
            sin_theta = math.sin(math.radians(angle))
            if sin_theta == 0:
                raise ValueError("Angle cannot be 0°!")
            return force / (self.g * sin_theta)
        elif scenario == "Pushing Object" and mu != 0:
            return force / (mu * self.g)
        else:
            raise ValueError("Cannot calculate mass with given parameters!")
    
    def calculate_motion(self, params):
        """
        Main physics calculation method
        Returns dictionary with all calculated values
        """
        scenario = params['scenario']
        F = params['F']
        d = params['d']
        m = params['m']
        angle = params['angle']
        mu = params['mu']
        force_angle = params['force_angle']
        
        solution_text = ""
        
        # Calculate mass if not provided
        if m is None:
            try:
                m = self.calculate_mass_from_force(F, scenario, angle, mu)
                solution_text += f"✓ Mass: m = {m:.2f} kg\n\n"
                params['m'] = m
            except ValueError as e:
                return {'moves': False, 'error': str(e), 'solution': solution_text}
        
        # Calculate forces
        weight = m * self.g
        Fn = self.calculate_normal_force(m, scenario, angle, F, force_angle)
        F_req = self.calculate_required_force(m, scenario, angle, mu, Fn)
        
        # Generate force formula text
        if scenario == "Lifting Object":
            formula = "F_req = m × g"
        elif scenario == "Inclined Plane":
            formula = f"F_req = m×g×sin({angle}°) + μ×Fn"
        else:
            formula = "F_req = μ × Fn"
        
        # Calculate applied force if not provided
        if F is None:
            F = F_req * 1.2
            solution_text += f"✓ Force: F = {F:.2f} N\n\n"
            params['F'] = F
        
        # Check if force is sufficient
        if F < F_req:
            solution_text += f"❌ INSUFFICIENT FORCE!\n\n"
            solution_text += f"Applied: {F:.2f} N\nRequired: {F_req:.2f} N\n"
            return {'moves': False, 'solution': solution_text, 'params': params}
        
        # Calculate net force
        net_force = self._calculate_net_force(F, F_req, scenario, angle, force_angle, weight, mu, Fn)
        
        # Calculate energy and motion
        net_work = net_force * d
        ke_final = max(net_work, 0)
        v_final = math.sqrt(2 * ke_final / m) if m > 0 and ke_final > 0 else 0
        
        # Build solution text
        solution_text += self._build_solution_text(
            m, F, d, mu, weight, Fn, F_req, formula, net_force, 
            net_work, ke_final, v_final, params.get('anim_speed', 1.0)
        )
        
        return {
            'moves': True,
            'solution': solution_text,
            'params': params,
            'F_req': F_req,
            'net_work': net_work,
            'ke_final': ke_final,
            'v_final': v_final,
            'power': net_work / (3.0 / params.get('anim_speed', 1.0)),
            'Fn': Fn
        }
    
    def _calculate_net_force(self, F, F_req, scenario, angle, force_angle, weight, mu, Fn):
        """Calculate net force in direction of motion"""
        F_parallel_applied = F * math.cos(math.radians(force_angle)) if scenario == "Pushing Object" else F
        F_parallel_gravity = weight * math.sin(math.radians(angle)) if scenario == "Inclined Plane" else 0
        F_friction = mu * Fn if scenario != "Lifting Object" else 0
        
        if scenario == "Lifting Object":
            net_force = F - weight
        elif scenario == "Inclined Plane":
            net_force = F - F_parallel_gravity - F_friction
        else:  # Pushing Object
            net_force = F_parallel_applied - F_friction
        
        if net_force < 0:
            net_force = 0
            if F > F_req and scenario != "Lifting Object" and scenario != "Inclined Plane":
                net_force = F - F_req
        
        return net_force
    
    def _build_solution_text(self, m, F, d, mu, weight, Fn, F_req, formula, 
                            net_force, net_work, ke_final, v_final, anim_speed):
        """Build formatted solution text"""
        time_interval = 3.0 / anim_speed
        power = net_work / time_interval if time_interval > 0 else 0
        
        text = f"📋 Given:\n"
        text += f"   m = {m:.2f} kg | F = {F:.2f} N | d = {d:.2f} m\n"
        text += f"   μ = {mu:.3f}\n\n"
        text += f"⚖️ Forces:\n"
        text += f"   Weight = {weight:.2f} N\n"
        text += f"   Normal = {Fn:.2f} N\n"
        text += f"   {formula} = {F_req:.2f} N\n"
        text += f"   Net = {net_force:.2f} N ✓\n\n"
        text += f"⚡ Energy:\n"
        text += f"   Net Work = {net_work:.2f} J\n"
        text += f"   ΔKE = {ke_final:.2f} J\n"
        text += f"   v = {v_final:.2f} m/s\n"
        text += f"   Power = {power:.2f} W\n"
        
        return text