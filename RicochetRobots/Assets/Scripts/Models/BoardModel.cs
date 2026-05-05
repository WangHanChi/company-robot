using System;

namespace RicochetRobots.Models
{
    [Flags]
    public enum WallDirection
    {
        None = 0,
        Top = 1,
        Right = 2,
        Bottom = 4,
        Left = 8
    }

    public class BoardModel
    {
        public const int Width = 16;
        public const int Height = 16;

        // true if there is a center piece 2x2 blocking area, but standard ricochet has a 2x2 center block.
        // We will just model walls for each cell.
        private WallDirection[,] grid;

        public BoardModel()
        {
            grid = new WallDirection[Width, Height];
            InitializeBorders();
            // TODO: Initialize specific board layouts (walls)
            InitializeCenterObstacle();
        }

        private void InitializeBorders()
        {
            for (int x = 0; x < Width; x++)
            {
                for (int y = 0; y < Height; y++)
                {
                    WallDirection walls = WallDirection.None;

                    if (y == Height - 1) walls |= WallDirection.Top;
                    if (x == Width - 1) walls |= WallDirection.Right;
                    if (y == 0) walls |= WallDirection.Bottom;
                    if (x == 0) walls |= WallDirection.Left;

                    grid[x, y] = walls;
                }
            }
        }

        private void InitializeCenterObstacle()
        {
            // The center 2x2 area is blocked. (7,7), (8,7), (7,8), (8,8)
            AddWall(7, 7, WallDirection.Right | WallDirection.Top);
            AddWall(8, 7, WallDirection.Left | WallDirection.Top);
            AddWall(7, 8, WallDirection.Right | WallDirection.Bottom);
            AddWall(8, 8, WallDirection.Left | WallDirection.Bottom);
        }

        public void AddWall(int x, int y, WallDirection wall)
        {
            if (IsValidPosition(x, y))
            {
                grid[x, y] |= wall;
                
                // Add reciprocal wall to neighbor
                if (wall.HasFlag(WallDirection.Top) && IsValidPosition(x, y + 1))
                    grid[x, y + 1] |= WallDirection.Bottom;
                if (wall.HasFlag(WallDirection.Bottom) && IsValidPosition(x, y - 1))
                    grid[x, y - 1] |= WallDirection.Top;
                if (wall.HasFlag(WallDirection.Right) && IsValidPosition(x + 1, y))
                    grid[x + 1, y] |= WallDirection.Left;
                if (wall.HasFlag(WallDirection.Left) && IsValidPosition(x - 1, y))
                    grid[x - 1, y] |= WallDirection.Right;
            }
        }

        public bool HasWall(int x, int y, WallDirection direction)
        {
            if (!IsValidPosition(x, y)) return true; // Out of bounds is considered a wall
            return grid[x, y].HasFlag(direction);
        }

        public bool IsValidPosition(int x, int y)
        {
            return x >= 0 && x < Width && y >= 0 && y < Height;
        }
    }
}
