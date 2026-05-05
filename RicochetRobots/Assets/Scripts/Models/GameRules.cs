using System.Collections.Generic;
using System.Linq;

namespace RicochetRobots.Models
{
    public static class GameRules
    {
        /// <summary>
        /// Calculates the final destination of a robot moving in a specific direction.
        /// </summary>
        public static (int X, int Y) CalculateDestination(RobotModel movingRobot, WallDirection direction, List<RobotModel> allRobots, BoardModel board)
        {
            int currentX = movingRobot.X;
            int currentY = movingRobot.Y;

            int dx = 0;
            int dy = 0;

            if (direction == WallDirection.Top) dy = 1;
            else if (direction == WallDirection.Bottom) dy = -1;
            else if (direction == WallDirection.Right) dx = 1;
            else if (direction == WallDirection.Left) dx = -1;
            else return (currentX, currentY);

            while (true)
            {
                // 1. Check if the current cell has a wall in the movement direction
                if (board.HasWall(currentX, currentY, direction))
                {
                    break;
                }

                int nextX = currentX + dx;
                int nextY = currentY + dy;

                // 2. Check if moving to the next cell would hit another robot
                if (allRobots.Any(r => r != movingRobot && r.X == nextX && r.Y == nextY))
                {
                    break;
                }

                // If no wall and no robot, move to the next cell and continue sliding
                currentX = nextX;
                currentY = nextY;
            }

            return (currentX, currentY);
        }
        
        /// <summary>
        /// Checks if the target is reached.
        /// </summary>
        public static bool IsTargetReached(RobotModel robot, int targetX, int targetY, RobotColor targetColor)
        {
            // If the target is a wildcard color or matches the robot's color
            // and the position matches.
            return (robot.Color == targetColor || targetColor == RobotColor.Silver /* Assuming Silver can be any or specific wildcard */) 
                   && robot.X == targetX 
                   && robot.Y == targetY;
        }
    }
}
