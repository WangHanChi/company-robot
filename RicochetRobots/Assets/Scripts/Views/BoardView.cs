using UnityEngine;
using RicochetRobots.Models;
using System.Collections.Generic;

namespace RicochetRobots.Views
{
    public class BoardView : MonoBehaviour
    {
        public GameObject wallPrefab; 
        public GameObject cellPrefab; 

        // Keep track of instantiated walls to prevent duplicates visually
        private HashSet<Vector2> spawnedWalls = new HashSet<Vector2>();

        public void Initialize(BoardModel boardModel)
        {
            for (int x = 0; x < BoardModel.Width; x++)
            {
                for (int y = 0; y < BoardModel.Height; y++)
                {
                    // Instantiate floor tile
                    if (cellPrefab != null)
                    {
                        Instantiate(cellPrefab, new Vector3(x, y, 0), Quaternion.identity, transform);
                    }

                    // Instantiate walls
                    if (boardModel.HasWall(x, y, WallDirection.Top))
                        CreateWall(x, y + 0.5f, true);
                    if (boardModel.HasWall(x, y, WallDirection.Bottom))
                        CreateWall(x, y - 0.5f, true);
                    if (boardModel.HasWall(x, y, WallDirection.Right))
                        CreateWall(x + 0.5f, y, false);
                    if (boardModel.HasWall(x, y, WallDirection.Left))
                        CreateWall(x - 0.5f, y, false);
                }
            }
        }

        private void CreateWall(float x, float y, bool isHorizontal)
        {
            if (wallPrefab == null) return;
            
            // Round to avoid float precision issues in HashSet
            Vector2 pos = new Vector2(Mathf.Round(x * 10f) / 10f, Mathf.Round(y * 10f) / 10f);
            
            if (!spawnedWalls.Contains(pos))
            {
                GameObject wall = Instantiate(wallPrefab, new Vector3(pos.x, pos.y, 0), Quaternion.identity, transform);
                if (!isHorizontal)
                {
                    wall.transform.rotation = Quaternion.Euler(0, 0, 90);
                }
                spawnedWalls.Add(pos);
            }
        }
    }
}
