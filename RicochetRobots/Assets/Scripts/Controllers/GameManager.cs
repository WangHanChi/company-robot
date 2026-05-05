using UnityEngine;
using RicochetRobots.Models;
using RicochetRobots.Views;
using System.Collections.Generic;

namespace RicochetRobots.Controllers
{
    public class GameManager : MonoBehaviour
    {
        public BoardView boardView;
        public GameObject robotPrefab;
        
        private BoardModel boardModel;
        private List<RobotModel> robots = new List<RobotModel>();
        private RobotModel selectedRobot;
        
        private int moveCount = 0;

        void Start()
        {
            InitializeGame();
        }

        void InitializeGame()
        {
            boardModel = new BoardModel();
            
            if (boardView != null)
            {
                boardView.Initialize(boardModel);
            }

            // Spawn 4 robots in corners for testing
            SpawnRobot(RobotColor.Red, 1, 1);
            SpawnRobot(RobotColor.Blue, 14, 1);
            SpawnRobot(RobotColor.Green, 1, 14);
            SpawnRobot(RobotColor.Yellow, 14, 14);
            
            // Set first selected robot
            if (robots.Count > 0)
            {
                selectedRobot = robots[0];
                Debug.Log("Game Initialized. Default robot selected: Red.");
            }
            
            // Camera Setup helper
            Camera.main.transform.position = new Vector3(BoardModel.Width / 2f - 0.5f, BoardModel.Height / 2f - 0.5f, -10);
            Camera.main.orthographicSize = BoardModel.Height / 2f + 1;
        }

        void SpawnRobot(RobotColor color, int x, int y)
        {
            RobotModel model = new RobotModel(color, x, y);
            robots.Add(model);

            if (robotPrefab != null)
            {
                GameObject robotObj = Instantiate(robotPrefab);
                RobotView view = robotObj.GetComponent<RobotView>();
                if (view != null)
                {
                    view.Initialize(model);
                }
            }
        }

        public void SelectRobotAt(int x, int y)
        {
            foreach (var robot in robots)
            {
                if (robot.X == x && robot.Y == y)
                {
                    selectedRobot = robot;
                    Debug.Log($"Selected {robot.Color} robot.");
                    return;
                }
            }
        }

        public void MoveSelectedRobot(WallDirection direction)
        {
            if (selectedRobot == null) return;

            var destination = GameRules.CalculateDestination(selectedRobot, direction, robots, boardModel);
            
            if (destination.X != selectedRobot.X || destination.Y != selectedRobot.Y)
            {
                selectedRobot.SetPosition(destination.X, destination.Y);
                moveCount++;
                Debug.Log($"Moved {selectedRobot.Color} to ({destination.X}, {destination.Y}). Total moves: {moveCount}");
            }
        }
    }
}
