import json
import random

ACTIONS = ( "accelerate", "slow_down", "turn_left", "turn_right" )


class QLearner:
    """ Q-learning with a linear function approximator: Q(s, a) = weights[a] . state
        No table, no neural net -- one weight vector per action, updated directly
        via the TD error each step (see the design discussion this came from). """

    def __init__(self, num_features, alpha=0.05, gamma=0.95,
                 epsilon=1.0, epsilon_min=0.05, epsilon_decay=0.995):
        self.alpha         = alpha          # learning rate
        self.gamma         = gamma          # discount factor
        self.epsilon       = epsilon        # exploration probability
        self.epsilon_min   = epsilon_min
        self.epsilon_decay = epsilon_decay  # applied once per EPISODE, not per step -- see decay_epsilon()
        self.weights = { action: [0.0] * num_features for action in ACTIONS }

        # Populated by choose_action(), read by the HUD to explain the last decision
        self.last_q_values  = { action: 0.0 for action in ACTIONS }
        self.last_was_random = False

    def q_values(self, state):
        return {
            action: sum( w * s for w, s in zip( self.weights[action], state ) )
            for action in ACTIONS
        }

    def choose_action(self, state):
        self.last_q_values = self.q_values( state )
        if random.random() < self.epsilon:
            self.last_was_random = True
            return random.choice( ACTIONS )
        self.last_was_random = False
        return max( self.last_q_values, key=self.last_q_values.get )

    def update(self, state, action, reward, next_state, done):
        target = reward
        if not done:
            next_q  = self.q_values( next_state )
            target += self.gamma * max( next_q.values() )

        current_q = sum( w * s for w, s in zip( self.weights[action], state ) )
        td_error  = target - current_q

        self.weights[action] = [
            w + self.alpha * td_error * s
            for w, s in zip( self.weights[action], state )
        ]

    def decay_epsilon(self):
        self.epsilon = max( self.epsilon_min, self.epsilon * self.epsilon_decay )

    def save(self, path):
        with open( path, "w" ) as f:
            json.dump( { "weights": self.weights, "epsilon": self.epsilon }, f )

    def load(self, path):
        try:
            with open( path, "r" ) as f:
                data = json.load( f )
        except FileNotFoundError:
            print( f"No saved weights found at {path}" )
            return
        self.weights = data["weights"]
        self.epsilon = data["epsilon"]
