using UnityEngine;
using RicochetRobots.Models;
using System.Collections;

namespace RicochetRobots.Views
{
    public class RobotView : MonoBehaviour
    {
        private RobotModel model;
        public float moveSpeed = 15f;

        public void Initialize(RobotModel robotModel)
        {
            model = robotModel;
            model.OnPositionChanged += HandlePositionChanged;
            
            // Set initial position
            transform.position = new Vector3(model.X, model.Y, 0);
            
            // Set color based on model
            SpriteRenderer sr = GetComponent<SpriteRenderer>();
            if (sr != null)
            {
                switch (model.Color)
                {
                    case RobotColor.Red: sr.color = Color.red; break;
                    case RobotColor.Blue: sr.color = Color.blue; break;
                    case RobotColor.Green: sr.color = Color.green; break;
                    case RobotColor.Yellow: sr.color = Color.yellow; break;
                    case RobotColor.Silver: sr.color = Color.gray; break;
                }
            }
        }

        private void OnDestroy()
        {
            if (model != null)
            {
                model.OnPositionChanged -= HandlePositionChanged;
            }
        }

        private void HandlePositionChanged(int newX, int newY)
        {
            StopAllCoroutines();
            StartCoroutine(SlideToPosition(new Vector3(newX, newY, 0)));
        }

        private IEnumerator SlideToPosition(Vector3 targetPos)
        {
            while (Vector3.Distance(transform.position, targetPos) > 0.01f)
            {
                transform.position = Vector3.MoveTowards(transform.position, targetPos, moveSpeed * Time.deltaTime);
                yield return null;
            }
            transform.position = targetPos;
        }
    }
}
