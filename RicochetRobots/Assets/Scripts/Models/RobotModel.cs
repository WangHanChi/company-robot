using System;

namespace RicochetRobots.Models
{
    public enum RobotColor
    {
        Red,
        Blue,
        Green,
        Yellow,
        Silver
    }

    public class RobotModel
    {
        public RobotColor Color { get; private set; }
        public int X { get; private set; }
        public int Y { get; private set; }

        public event Action<int, int> OnPositionChanged;

        public RobotModel(RobotColor color, int startX, int startY)
        {
            Color = color;
            X = startX;
            Y = startY;
        }

        public void SetPosition(int newX, int newY)
        {
            if (X != newX || Y != newY)
            {
                X = newX;
                Y = newY;
                OnPositionChanged?.Invoke(X, Y);
            }
        }
    }
}
