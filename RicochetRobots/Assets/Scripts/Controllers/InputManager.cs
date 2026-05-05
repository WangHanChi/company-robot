using UnityEngine;
using RicochetRobots.Models;

namespace RicochetRobots.Controllers
{
    public class InputManager : MonoBehaviour
    {
        public GameManager gameManager;
        
        private Vector2 swipeStart;
        private bool isSwiping = false;

        void Update()
        {
            if (gameManager == null) return;

            HandleKeyboardInput();
            HandleMouseInput();
        }

        void HandleKeyboardInput()
        {
            if (Input.GetKeyDown(KeyCode.UpArrow) || Input.GetKeyDown(KeyCode.W))
                gameManager.MoveSelectedRobot(WallDirection.Top);
            if (Input.GetKeyDown(KeyCode.DownArrow) || Input.GetKeyDown(KeyCode.S))
                gameManager.MoveSelectedRobot(WallDirection.Bottom);
            if (Input.GetKeyDown(KeyCode.RightArrow) || Input.GetKeyDown(KeyCode.D))
                gameManager.MoveSelectedRobot(WallDirection.Right);
            if (Input.GetKeyDown(KeyCode.LeftArrow) || Input.GetKeyDown(KeyCode.A))
                gameManager.MoveSelectedRobot(WallDirection.Left);
        }

        void HandleMouseInput()
        {
            if (Input.GetMouseButtonDown(0))
            {
                Vector3 mousePos = Camera.main.ScreenToWorldPoint(Input.mousePosition);
                int clickX = Mathf.RoundToInt(mousePos.x);
                int clickY = Mathf.RoundToInt(mousePos.y);
                
                gameManager.SelectRobotAt(clickX, clickY);
                
                swipeStart = Input.mousePosition;
                isSwiping = true;
            }
            
            if (Input.GetMouseButtonUp(0) && isSwiping)
            {
                isSwiping = false;
                Vector2 swipeEnd = Input.mousePosition;
                Vector2 swipeDelta = swipeEnd - swipeStart;
                
                if (swipeDelta.magnitude > 50f) // Minimum swipe distance
                {
                    if (Mathf.Abs(swipeDelta.x) > Mathf.Abs(swipeDelta.y))
                    {
                        if (swipeDelta.x > 0) gameManager.MoveSelectedRobot(WallDirection.Right);
                        else gameManager.MoveSelectedRobot(WallDirection.Left);
                    }
                    else
                    {
                        if (swipeDelta.y > 0) gameManager.MoveSelectedRobot(WallDirection.Top);
                        else gameManager.MoveSelectedRobot(WallDirection.Bottom);
                    }
                }
            }
        }
    }
}
